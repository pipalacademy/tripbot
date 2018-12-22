"""
tripbot
~~~~~~~

Program to download invoices from cleartrip for business account and
convert them into pdf.

USAGE:

To download all invocies:

    python tripbot.py download-invoices \
        --host pipal.cleartripforbusiness.com \
        --email tripbot@pipal.in \
        --password secret

CHANGES:
2018-12-22: v0.1 - first working version

"""
import re
import yaml
import io
import requests
import os
import subprocess
import click
import getpass
import sys

__author__ = "Anand Chitipothu <anandology@gmail.com>"
__version__ = "0.1"

class Cleartrip:
    """Class to interact with Cleartrip for busness website.
    """
    def __init__(self, host):
        self.host = host
        self.session = requests.session()

    def login(self, email, password):
        """Logs in to the website.

        On successful login, the cookies set by the site are stored in
        the session and will be used for subsequent requests.

        An exception is raised if login fails.
        """
        print("Logging in...")
        params = {
            "email": email,
            "password": password
        }
        response = self.post('/signIn', params)
        # The successful login redirects to a new page
        # Being on the same page is an indication of login failure.
        if response.url.endswith('/signIn'):
            raise Exception("Login failed")
        print("Log in successful!")

    def post(self, path, params):
        url = "https://{}{}".format(self.host, path)
        return self.session.post(url, params)

    def get(self, path, **kwargs):
        url = "https://{}{}".format(self.host, path)
        return self.session.get(url, **kwargs)

    def get_completed_trips(self):
        print("Getting the completed trips...")
        response = self.get("/dashboard/index?param=completed")

        # Replace newlines and tabs so that re and yaml can handle
        # this text
        html = response.text.replace("\n", " ").replace("\t", " ")
        m = re.search("var tripInfo = (.*]);", html)
        trips_js = m.group(1)

        # The trips_js is a valid JS but not valid json.
        # It doesn't use quotes for keys in objects.
        # So JSON won't be able to parse it, but YAML will.
        trips = yaml.safe_load(io.StringIO(trips_js))

        print("Found {} trips.".format(len(trips)))
        return [Trip(self, info) for info in trips]

class Trip:
    """Models a trip object.
    """
    def __init__(self, cleartrip, trip_info):
        self.cleartrip = cleartrip
        self.info = trip_info
        self.id = self.info['id']
        self.type = self.info['type']
        self.name = self.info['name']
        self.invoice_html = None

    def __repr__(self):
        return "<Trip#{}: {!r}>".format(self.id, self.name)

    def download_invoice(self, output_file):
        print("Downloading the invoice for trip {} - {!r}".format(self.id, self.name))
        html = self.get_invoice_html()
        with open(output_file, "w") as f:
            f.write(html)

    def get_invoice_html(self):
        if self.invoice_html is None:
            path = "/trips/{}/invoice".format(self.id)
            self.invoice_html = self.cleartrip.get(path).text
        return self.invoice_html

    def download_invoice_as_pdf(self, output_file=None):
        if output_file is None:
            output_file = "trip-{}-invoice.pdf".format(self.id)
        html_file =  "trip-{}-invoice.html".format(self.id)
        self.download_invoice(html_file)
        print("Converting the invoice to PDF...")
        self.print_to_pdf(html_file, output_file)
        os.remove(html_file)

    def print_to_pdf(self, html_file, pdf_file):
        """Prints the HTML to pdf using chrome headless
        """
        if sys.platform == "darwin":
            CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        else:
            # TODO: Add support for chromium
            CHROME = "chrome"
        cmd = [
            CHROME,
            "--headless",
            "--disable-gpu",
            "--no-margins",
            "--print-to-pdf",
            html_file
        ]
        subprocess.check_call(cmd)
        os.rename("output.pdf", pdf_file)
        print("generated", pdf_file)

@click.group()
def cli():
    pass

@cli.command()
@click.option("--host",
    help="hostname of the cleartripforbusiness website",
    required=True)
@click.option("--email", required=True)
@click.option("--password", help="password to login. Can be provided as argument or on prompt.")
def download_invoices(host, email, password=None):
    """Downloads all invoices.
    """
    if password is None:
        password = getpass.getpass("Password:")
    cleartrip = Cleartrip(host)
    cleartrip.login(email, password)
    for trip in cleartrip.get_completed_trips():
        trip.download_invoice_as_pdf()

def main():
    cli()

if __name__ == '__main__':
    main()
