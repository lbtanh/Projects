# t2.micro, 85Gb gp2 volume

import os
import sys
import boto3

pywren_bucket = 'pywren1'
s3            = boto3.resource('s3')
client        = boto3.client('s3')

def split_tsv_file(tsv_filename):

  def line_manipulation(line_to_manipulate):

    line_to_manipulate = 'prefix: ' + line_to_manipulate + '\n'

    return line_to_manipulate

  build_file = ''
  file_count = 0
  line_count = 0
  obj        = s3.Object(pywren_bucket, tsv_filename) #obj.key)
  body       = obj.get()['Body']
  blocksize  = 1024*1024
  buf        = body.read(blocksize)

  while len(buf) > 0:

    lines = buf.split('\n')

    for line in lines:

      if line.count('\t') > 13:

        if line_count < 99999:

          line_count   += 1
          build_file    = build_file + line_manipulation(line)

        else:

          build_file    = build_file + line_manipulation(line)
          file_number   = "%05d" % file_count
          client.put_object(Body=build_file, Bucket=pywren_bucket, Key=obj.key + '_' + file_number)
          print obj.key + '_' + file_number
          build_file    = ''
          line_count    = 0
          file_count   += 1

    if line.count('\t') < 14:
      buf = line + body.read(blocksize)
    else:
      buf = body.read(blocksize)

  if line_count > 0:
    file_number   = "%05d" % file_count
    client.put_object(Body=build_file, Bucket=pywren_bucket, Key=obj.key + '_' + file_number)
    print obj.key + '_' + file_number
    build_file    = ''
    line_count    = 0
    file_count   += 1

#for obj in s3.Bucket(pywren_bucket).objects.all():


if __name__ == '__main__':

  for obj in s3.Bucket('amazon-reviews-pds').objects.all():
    if obj.key[:3] == 'tsv' and len(obj.key) > 4:
      cmd = 'aws s3 cp s3://amazon-reviews-pds/' + obj.key + ' /home/ec2-user/'
      print cmd
#      os.system(cmd)

  cmd = 'gunzip /home/ec2-user/*.gz'
  print cmd
#  os.system(cmd)

  for root, dirs, files in os.walk('/home/ec2-user/'):
    for filename in files:
      if filename[-3:] == 'tsv':
        print filename

  split_tsv_file('amazon_reviews_us_Gift_Card_v1_00.tsv')
