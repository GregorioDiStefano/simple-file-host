Simple HTTP app I can use to POST files to from cURL, and get a download URL.
Useful when copy a small file to a machine that doesn't have OpenSSH (or Windows)

I use: curl -F "userid=1" -F "filecomment=This is an image file" -F "file=@dice.py" <domain>
