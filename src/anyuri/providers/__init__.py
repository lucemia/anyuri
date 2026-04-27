"""
anyuri cloud provider URI types.

Importing from this module registers the providers with AnyUri automatically:

    >>> from anyuri.providers import GSUri, S3Uri
    >>> from anyuri import AnyUri
    >>> AnyUri("gs://bucket/key.jpg")
    GSUri("gs://bucket/key.jpg")
"""

from anyuri.providers._azure import AzureUri
from anyuri.providers._gcs import GSUri
from anyuri.providers._r2 import R2Uri
from anyuri.providers._s3 import S3Uri

__all__ = ["GSUri", "S3Uri", "AzureUri", "R2Uri"]
