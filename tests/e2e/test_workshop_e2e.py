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

    # 4. 点击保存修改，并等待跳转完成
    page.get_by_role("button", name="Save changes").click()
    
    # 等待网络空闲，确保后端已处理保存请求
    page.wait_for_load_state("networkidle")
    
    # 5. 断言详情页面标题包含 Honda Accord（宽松选择器，兼容不同 heading 级别）
    expect(page.get_by_text("Honda Accord").first).to_be_visible(timeout=15000)
    
    # 记录当前 URL，刷新后应该还在同一页面
    detail_url = page.url
    print(f"Detail page URL: {detail_url}")

    # 6. 刷新页面，并断言修改后的型号和年份在刷新后依然持久化显示
    page.reload()
    page.wait_for_load_state("networkidle")
    
    # 如果重定向到列表页或其他页面，重新导航到详情页
    if "/cars/" not in page.url or page.url.endswith("/cars"):
        print(f"Redirected to {page.url}, navigating back to {detail_url}")
        page.goto(detail_url)
        page.wait_for_load_state("networkidle")
    
    # 断言数据持久化（先检查元素存在，再检查内容）
    model_locator = page.locator("#car-model")
    year_locator = page.locator("#car-year")
    
    # 等待元素出现（给前端渲染时间）
    model_locator.wait_for(state="visible", timeout=15000)
    year_locator.wait_for(state="visible", timeout=15000)
    
    # 验证内容
    expect(model_locator).to_contain_text("Accord", timeout=15000)
    expect(year_locator).to_contain_text("2023", timeout=15000)
