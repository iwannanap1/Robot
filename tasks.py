from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Created ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    close_annoying_modal()
    download_order_files()
    read_as_a_table()
    archive_receipts()

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_order_files():
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

def order_another_robot():
    page = browser.page()
    page.click("#order-another")
    close_annoying_modal()

def read_as_a_table():
    robot = Tables()
    orders = robot.read_table_from_csv(
        "orders.csv", columns=["Order Number", "Head", "Body", "Legs", "Address"]
    )
    for row in orders:
        fill_the_form(row)
       
def close_annoying_modal():
    page = browser.page()
    page.click("text=OK")

def fill_the_form(row):
    page = browser.page()

    page.fill("#address",row["Address"])
    page.select_option("#head", row["Head"])
    page.locator('.form-control').nth(0).fill(row["Legs"])
    page.locator(f".form-check-input[value='{row['Body']}']").check()
    page.click("#preview")
    try:
        page.click("#order")
    except Exception as e:
        print(f"error occured: {e}. Retrying...")
        page.click("#order")
    order_another = page.query_selector("#order-another")
    if order_another:
        pdf_path = store_order_receipt(row["Order Number"])
        screenshot_path = screenshot_robot(row["Order Number"])
        embed_screenshot_to_receipt(screenshot_path, pdf_path)
        order_another_robot()
        # close_annoying_modal()
      
def store_order_receipt(order_number):
    page=browser.page()
    orders_html = page.locator("#receipt").inner_html()

    pdf=PDF()
    pdf_path=f"output/receipts/{order_number}.pdf"
    pdf.html_to_pdf(orders_html, pdf_path)
    return pdf_path

def screenshot_robot(order_number):
    page= browser.page()
    robot_preview = page.locator("#robot-preview-image")
    ss_path = f"output/screenshots/{order_number}.png"
    robot_preview.screenshot(path = ss_path)
    return ss_path

def embed_screenshot_to_receipt(ss_path, pdf_path):
    pdf=PDF()
    pdf.add_watermark_image_to_pdf(image_path=ss_path,
                             source_path=pdf_path,
                             output_path = pdf_path)
    
def archive_receipts():
    lib=Archive()
    lib.archive_folder_with_zip('./output/receipts', './output/receipts.zip')