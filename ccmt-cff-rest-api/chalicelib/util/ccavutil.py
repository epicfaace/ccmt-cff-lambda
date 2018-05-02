from Crypto.Cipher import AES
import hashlib
from urllib.parse import urlencode, parse_qsl
import binascii

POSSIBLE_PARAMS = ["merchant_id", "order_id", "currency", "amount", "redirect_url", "cancel_url", "language", "billing_name", "billing_address", "billing_city", "billing_state", "billing_zip", "billing_country", "billing_tel", "billing_email", "delivery_name", "delivery_address", "delivery_city", "delivery_state", "delivery_zip", "delivery_country", "delivery_tel", "merchant_param1", "merchant_param2", "merchant_param3", "merchant_param4", "merchant_param5", "integration_type", "promo_code", "customer_identifier"]

def pad(data):
  length = 16 - (len(data) % 16)
  data += bytes([length])*length
  return data

def encrypt(inputDict,workingKey):
  iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
  plainText = urlencode(inputDict)
  plainText = pad(plainText.encode('latin-1'))
  encDigest = hashlib.md5() # bytes("text","ascii")
  encDigest.update(workingKey)
  enc_cipher = AES.new(encDigest.digest(), AES.MODE_CBC, iv.encode('latin-1'))
  encryptedText = enc_cipher.encrypt(plainText)
  return binascii.hexlify(encryptedText)

def decrypt(cipherText,workingKey):
  iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
  decDigest = hashlib.md5() #md5.new ()
  decDigest.update(workingKey)
  encryptedText = binascii.unhexlify(cipherText)
  dec_cipher = AES.new(decDigest.digest(), AES.MODE_CBC, iv.encode('latin-1'))
  decryptedText = dec_cipher.decrypt(encryptedText).decode('utf-8')
  return dict(parse_qsl(decryptedText))