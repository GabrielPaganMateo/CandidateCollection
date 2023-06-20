from storages.backends.s3boto3 import S3Boto3Storage
import sys
import os

class S3Storage(S3Boto3Storage):
    """
    This is our custom version of S3Boto3Storage that fixes a bug in
    boto3 where the passed in file is a SpooledTemporaryFile.
    """
    def _save(self, name, content):
        if 'boto3.s3.transfer' in sys.modules:
            from boto3.s3.transfer import TransferConfig
            boto3_transfer = sys.modules['boto3.s3.transfer']
            if hasattr(boto3_transfer, 'S3Transfer'):
                # boto3 version 1.3.0 to 1.3.1, inclusive
                S3Transfer = boto3_transfer.S3Transfer
            else:
                # boto3 version 1.4.0 and up.
                from boto3.s3.transfer import S3Transfer
        else:
            from boto3.s3.transfer import S3Transfer  # boto3 version 1.2.3

        if not hasattr(content, 'seek'):
            content.open()

        content.seek(0, os.SEEK_SET)

        # setting the content_type in the key object is not enough.
        headers = {'Content-Type': content.content_type}

        # setting the content_disposition in the key object is not enough.
        if hasattr(content.file, 'content_disposition'):
            headers['Content-Disposition'] = content.file.content_disposition

        transfer = S3Transfer(self.connection)
        transfer.upload_file(
            filename=content.name,
            bucket=self.bucket_name,
            key=self._encode_name(name),
            callback=None, # We can't use content.tell() as a callback because it causes a deadlock
            extra_args=headers,
            config=TransferConfig()
        )
        return name