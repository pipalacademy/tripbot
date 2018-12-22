# tripbot

Script to download trip invoices from cleartrip business account.

[Cleartrip for Business][1] is a wonderful service for managing flight and hotel bookings if you are a small organization. However, downloading invoices every month for filing GST returns is a big pain. Their UI is clumky and takes lot of time to download all invocies. This utility solves that problem by automating the downloads and also converting them to PDF using chrome headless.

[1]: https://www.cleartripforbusiness.com/

## Usage

    $ python tripbot.py download-invoices \
        --host pipal.cleartripforbusiness.com \
        --email tripbot@pipal.in
   	Password: ******
	Logging in...
	Log in sucessful!
	Getting the completed trips...
	Found 5 trips.
	Downloading the invoice for trip 18112812345 - 'Visakhapatnam - Bangalore one-way'
	Converting the invoice to PDF...
	Generated trip-18112846320-invoice.pdf
	...
	