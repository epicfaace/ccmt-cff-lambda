import os
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
# import bleach
import html2text
from pynliner import Pynliner
from .util import format_paymentInfo, format_payment, display_form_dict

ccmt_email_css = """
table {
    border: 1px dashed black;
}
table th {
    text-transform: capitalize;
}
table th, table td {
    padding: 5px;
}
ul {
    list-style-type: none;
    padding: 0;
}
img.mainImage {
    max-width: 200px;
    float: right;
    margin: 20px;
}
"""

def send_confirmation_email(response, confirmationEmailInfo):
    if confirmationEmailInfo:
        toField = confirmationEmailInfo["toField"]
        msgBody = ""
        if "contentHeader" in confirmationEmailInfo:
            msgBody += confirmationEmailInfo["contentHeader"]
        msgBody += "<h1>{}</h1>".format(confirmationEmailInfo.get("subject", "") or confirmationEmailInfo.get("header", "") or "Confirmation Email")
        if "image" in confirmationEmailInfo:
            msgBody += "<img class='mainImage' src='{}' />".format(confirmationEmailInfo["image"])
        msgBody += confirmationEmailInfo.get("message", "")
        if confirmationEmailInfo["showResponse"]:
            msgBody += "<br><br>" + display_form_dict(response["value"])
        
        if 'items' in response['paymentInfo'] and len(response['paymentInfo']['items']) > 0:
            msgBody += "<br><br><table class=paymentInfoTable>"
            msgBody += "<tr><th>Name</th><th>Description</th><th>Amount</th><th>Quantity</th></tr>"
            for paymentInfoItem in response['paymentInfo']['items']:
                msgBody += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                    paymentInfoItem.get('name',''),
                    paymentInfoItem.get('description',''),
                    format_payment(paymentInfoItem.get('amount',''), 'USD'),
                    paymentInfoItem.get('quantity','')
                )
            msgBody += "</table>"
        
        msgBody += "<br><br><h2>Total Amount: {}</h2><br><h2>Amount Received: {}</h2>".format(format_paymentInfo(response["paymentInfo"]), format_payment(response.get("IPN_TOTAL_AMOUNT", 0), 'USD'))
        if confirmationEmailInfo["showModifyLink"] and "modifyLink" in response:
            msgBody += "<br><br>Modify your response by going to this link: {}#responseId={}".format(response["modifyLink"], str(response["responseId"]))
        if "contentFooter" in confirmationEmailInfo:
            msgBody += confirmationEmailInfo["contentFooter"]
        # todo: check amounts and Completed status, and then send.
        send_email(toEmail=response["value"][toField],
                            fromEmail=confirmationEmailInfo.get("from", "webmaster@chinmayamission.com"),
                            fromName=confirmationEmailInfo.get("fromName", "Webmaster"),
                            subject=confirmationEmailInfo.get("subject", "Confirmation Email"),
                            msgBody=msgBody)
def send_partial_payment_email(payment_info_old, payment_info_new, response, confirmationEmailInfo):
    pass
    """if "confirmationEmailInfo" in response and confirmationEmailInfo:
        toField = confirmationEmailInfo["toField"]
        
        # todo: check amounts and Completed status, and then send.
        send_email(toEmail=response["value"][toField],
                            fromEmail=confirmationEmailInfo.get("from", "webmaster@chinmayamission.com"),
                            fromName=confirmationEmailInfo.get("fromName", "Webmaster"),
                            subject=confirmationEmailInfo.get("subject", "Confirmation Email"),
                            msgBody=msgBody)
    """
def send_update_notification_email(payment_info_old, payment_info_new, response, confirmationEmailInfo):
    # Not used.
    if confirmationEmailInfo:
        toField = confirmationEmailInfo["toField"]
        amount_owed = 0
        if payment_info_old["currency"] == payment_info_new["currency"]:
            amount_owed = float(payment_info_new["total"] - payment_info_old["total"])
        amount_owed_string = "Amount Owed: {}".format(amount_owed) if amount_owed else ""
        msgBody = """You have changed your registration information.<br>
        <b>Please note that you must complete payment to continue.</b><br><br>
        Original Amount: {}<br>
        New Amount: {}<br>
        {}<br>
        """.format(format_paymentInfo(payment_info_old), format_paymentInfo(payment_info_new), amount_owed_string)
        # todo: check amounts and Completed status, and then send.
        send_email(toEmail=response["value"][toField],
                            fromEmail=confirmationEmailInfo.get("from", "webmaster@chinmayamission.com"),
                            fromName=confirmationEmailInfo.get("fromName", "Webmaster"),
                            subject=confirmationEmailInfo.get("subject", "Confirmation Email") + " - Payment Required",
                            msgBody=msgBody)
def send_email(
    toEmail="aramaswamis@gmail.com",
    fromEmail="webmaster@chinmayamission.com",
    fromName="Webmaster",
    subject="Confirmation email",
    msgBody="<h1>Confirmation</h1><br><p>Thank you for registering.</p>"
    ):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "{} <{}>".format(fromName, fromEmail)

    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = toEmail

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    # CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"

    # The subject line for the email.
    SUBJECT = subject

    # The full path to the file that will be attached to the email.
    # ATTACHMENT = "path/to/customers-to-contact.xlsx"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = html2text.html2text(msgBody)

    # The HTML body of the email.
    BODY_HTML = Pynliner().from_string(msgBody).with_cssString(ccmt_email_css).run() # bleach.linkify(bleach.clean(msgBody))

    # The character encoding for the email.
    CHARSET = "utf-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)

    # Create a multipart/mixed parent container.
    msg = MIMEMultipart('mixed')
    # Add subject, from and to lines.
    msg['Subject'] = SUBJECT 
    msg['From'] = SENDER 
    msg['To'] = RECIPIENT

    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart('alternative')

    # Encode the text and HTML content and set the character encoding. This step is
    # necessary if you're sending a message with characters outside the ASCII range.
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)

    # Add the text and HTML parts to the child container.
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)

    # Define the attachment part and encode it using MIMEApplication.
    # att = MIMEApplication(open(ATTACHMENT, 'rb').read())

    # Add a header to tell the email client to treat this part as an attachment,
    # and to give the attachment a name.
    # att.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT))

    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container.
    msg.attach(msg_body)

    # Add the attachment to the parent container.
    # msg.attach(att)
    #print(msg)
    #try:
        #Provide the contents of the email.
    response = client.send_raw_email(
        Source=SENDER,
        Destinations=[
            RECIPIENT
        ],
        RawMessage={
            'Data': msg.as_string(),
        },
        # ConfigurationSetName=CONFIGURATION_SET
    )
    # Display an error if something goes wrong.	
    #except ClientError as e:
    #    print(e.response['Error']['Message'])
    #else:
    #    print("Email sent! Message ID:"),
    #    print(response['ResponseMetadata']['RequestId'])