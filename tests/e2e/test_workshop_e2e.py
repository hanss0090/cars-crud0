import re
from playwright.sync_api import expect
def test_user_creates_car_in_browser(page, live_server):
    page.goto(f"{live_server}/cars/new")

    page.get_by_label("Make", exact=True).fill("Toyota")
    page.get_by_label("Model", exact=True).fill("Yaris")
    page.get_by_label("Year", exact=True).fill("2020")
    page.get_by_label("Color", exact=False).fill("Blue")
    page.get_by_role("button", name="Create").click()
    expect(page).to_have_url(re.compile(r"/cars/\d+$"))
    expect(page.get_by_role("heading", name="Toyota Yaris")).to_be_visible()
def test_user_edits_car_and_change_survives_reload(page, live_server):
    # 1. 打开 /cars/new 并创建一辆 2022 年的 Honda Civic
    page.goto(f"{live_server}/cars/new")
    page.get_by_label("Make", exact=True).fill("Honda")
    page.get_by_label("Model", exact=True).fill("Civic")
    page.get_by_label("Year", exact=True).fill("2022")
    page.get_by_label("Color", exact=False).fill("Silver")
    page.get_by_role("button", name="Create car").click()

    # 2. 点击“Edit car”链接进入编辑页面
    page.get_by_role("link", name="Edit car").click()

    # 3. 将型号修改为 Accord，年份修改为 2023
    page.get_by_label("Model", exact=True).fill("Accord")
    page.get_by_label("Year", exact=True).fill("2023")

    # 4. 点击保存修改
    page.get_by_role("button", name="Save changes").click()

    # 5. 断言详情页面标题包含 Honda Accord
    expect(page.get_by_role("heading", name="Honda Accord")).to_be_visible()

    # 6. 刷新页面，并断言修改后的型号和年份在刷新后依然持久化显示
    page.reload()
    expect(page.locator("#car-model")).to_contain_text("Accord")
    expect(page.locator("#car-year")).to_contain_text("2023")
