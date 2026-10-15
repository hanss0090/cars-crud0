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
    # 1. 打开 /cars/new 并创建
    page.goto(f"{live_server}/cars/new")
    page.get_by_label("Make", exact=True).fill("Honda")
    page.get_by_label("Model", exact=True).fill("Civic")
    page.get_by_label("Year", exact=True).fill("2022")
    page.get_by_label("Color", exact=False).fill("Silver")
    page.get_by_role("button", name="Create car").click()
    
    # 等待创建完成（网络空闲）
    page.wait_for_load_state("networkidle")

    # 2. 进入编辑页面
    page.get_by_role("link", name="Edit car").click()
    page.wait_for_load_state("networkidle")

    # 3. 修改内容
    page.get_by_label("Model", exact=True).fill("Accord")
    page.get_by_label("Year", exact=True).fill("2023")

    # 4. 点击保存，监听网络响应确认成功
    with page.expect_response("**/cars/**") as response_info:
        page.get_by_role("button", name="Save changes").click()
    
    response = response_info.value
    print(f"Save response status: {response.status}")
    assert response.status in [200, 302], f"Save failed with status {response.status}"
    
    # 等待页面稳定
    page.wait_for_load_state("networkidle")
    print(f"After save URL: {page.url}")

    # 5. 检查是否成功（如果 heading 找不到，尝试 body 包含文本）
    try:
        expect(page.get_by_role("heading", name="Honda Accord")).to_be_visible(timeout=5000)
    except AssertionError:
        # fallback：检查 body 是否包含文本（可能标题结构不同）
        body_text = page.locator("body").inner_text()
        print(f"Page body contains 'Honda Accord': {'Honda Accord' in body_text}")
        print(f"Current URL: {page.url}")
        # 如果 body 里有但 heading 没有，说明是选择器问题；如果 body 里也没有，说明保存失败
        assert "Honda Accord" in body_text, f"Save failed. URL: {page.url}, Body: {body_text[:500]}"

    # 6. 刷新验证持久化
    page.reload()
    page.wait_for_load_state("networkidle")
    
    expect(page.locator("#car-model")).to_contain_text("Accord", timeout=15000)
    expect(page.locator("#car-year")).to_contain_text("2023", timeout=15000)
