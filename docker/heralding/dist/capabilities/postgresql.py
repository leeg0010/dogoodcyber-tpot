import struct
import logging
import asyncio
import random

from heralding.capabilities.handlerbase import HandlerBase

logger = logging.getLogger(__name__)

# Weak credential pairs for selective acceptance (Priority 2)
VALID_CREDENTIALS = [
    ('postgres', 'postgres123'),
    ('postgres', 'P@ssw0rd2024!'),
    ('dbadmin', 'Welcome1'),
]

# Immediate honeypot test rejections
HONEYPOT_TESTS = [
    ('postgres', 'postgres'),
    ('admin', 'admin'),
    ('test', 'test'),
    ('user', 'user'),
]

class PostgreSQL(HandlerBase):

  async def execute_capability(self, reader, writer, session):
    try:
      await self._handle_session(session, reader, writer)
    except struct.error as exc:
      logger.debug('PostgreSQL connection error: %s', exc)
      session.end_session()

  async def _handle_session(self, session, reader, writer):
    # Add realistic connection delay (0.5-1.5s)
    await asyncio.sleep(random.uniform(0.5, 1.5))
    
    # Read (we blindly assume) SSL request and deny it
    await read_msg(reader, writer)

    writer.write(b'N')

    session.activity()

    # Read login details
    data = await read_msg(reader, writer)
    login_dict = parse_dict(data)

    # Request plain text password login
    password_request = [b'R', 8, 3]
    writer.write(struct.pack('>c I I', *password_request))
    await writer.drain()

    # Add delay before password prompt (realistic)
    await asyncio.sleep(random.uniform(0.3, 0.7))

    # Read password
    data = await read_msg(reader, writer)
    password = parse_str(data)
    username = login_dict['user']
    
    # Check if honeypot test (immediate rejection, no logging noise)
    is_honeypot_test = (username, password) in HONEYPOT_TESTS
    
    if not is_honeypot_test:
        session.add_auth_attempt('plaintext', username=username, password=password)
    
    # Authentication processing delay (1.5-2.5s for realistic hashing simulation)
    await asyncio.sleep(random.uniform(1.5, 2.5))
    
    # Add failure penalty (extra 0.5-1s for failed auth)
    await asyncio.sleep(random.uniform(0.5, 1.0))

    # Report login failure with PostgreSQL 14.10 version string
    writer.write(b'E')
    fail = [
        b'SFATAL\x00C28P01\x00',
        'Mpassword authentication failed for user "{}"'.format(username).encode(
            'utf-8'),
        b'\x00Fauth.c\x00L335\x00Rauth_failed\x00',  # Updated line number for PG 14.10
        b'Vpostgresql 14.10\x00\x00',  # Version hint
    ]

    length = sum([len(f) for f in fail])
    writer.write(struct.pack('>I', length + 4))
    for f in fail:
      writer.write(f)

    await writer.drain()

    session.end_session()


async def read_msg(reader, writer):
  i = await reader.read(4)
  length = struct.unpack('>I', i)[0]
  data = await reader.read(length)
  return data


def parse_dict(data):
  dct = {}
  mode = 'pad'
  key = []
  value = []

  for c in struct.iter_unpack('c', data):
    c = c[0]

    if mode == 'pad':
      if c in (bytes([0]), bytes([3])):
        continue
      else:
        mode = 'key'

    if mode == 'key':
      if c == bytes([0]):
        mode = 'value'
      else:
        key.append(c.decode())

    elif mode == 'value':
      if c == bytes([0]):
        dct[''.join(key)] = ''.join(value)
        key = []
        value = []
        mode = 'pad'
      else:
        value.append(c.decode())

  return dct


def parse_str(data):
  data_array = bytearray(data)
  return data_array[1:-1].decode('utf-8')
