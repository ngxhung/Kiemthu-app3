# week06_app3_scroll_screenshot.py
# Tuần 6 - App 3: Cuộn danh sách & chụp màn hình (Swag Labs - PRODUCTS)
# Tài liệu: 8.3 Scroll, 8.7 Screenshot, 7.19 Remote WebDriver, 7.20 WebElement
# Hàm dùng: execute_script (mobile: scrollGesture), ANDROID_UIAUTOMATOR, UiScrollable,
#           find_elements, save_screenshot, screenshot (element)
#
# Cấu hình + locator đăng nhập lấy y hệt test_login.py (tuần 5) đã chạy được.

import os

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

USERNAME_HOP_LE = "standard_user"
PASSWORD_HOP_LE = "secret_sauce"

SP_DAU = "Sauce Labs Backpack"
SP_CUOI = "Test.allTheThings() T-Shirt (Red)"

THU_MUC_ANH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")

# Locator màn Products (đúng như app 2.7.1: RN dùng content-desc "test-...")
MAN_PRODUCTS = (AppiumBy.ACCESSIBILITY_ID, "test-PRODUCTS")
TEN_SAN_PHAM = (AppiumBy.ACCESSIBILITY_ID, "test-Item title")


@pytest.fixture
def driver():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "emulator-5554"
    options.app = r"F:\App\Android.SauceLabs.Mobile.Sample.app.2.7.1.apk"
    options.no_reset = True
    options.app_wait_activity = "com.swaglabsmobileapp.*"

    drv = webdriver.Remote("http://127.0.0.1:4723", options=options)
    os.makedirs(THU_MUC_ANH, exist_ok=True)
    yield drv
    drv.quit()


def dang_nhap(driver):
    """Đăng nhập nếu đang ở màn login; nếu app còn đang ở Products thì bỏ qua."""
    try:
        o_username = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "test-Username"))
        )
    except TimeoutException:
        o_username = None

    if o_username is not None:
        o_username.send_keys(USERNAME_HOP_LE)
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Password").send_keys(PASSWORD_HOP_LE)
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-LOGIN").click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(MAN_PRODUCTS))


@pytest.fixture
def man_products(driver):
    """Mỗi test bắt đầu từ màn Products đã đăng nhập, danh sách ở đầu trang."""
    dang_nhap(driver)
    cuon_len_dau(driver)
    return driver


def ten_dang_hien(driver):
    """Tên các sản phẩm đang hiện trên màn hình."""
    return [e.text for e in driver.find_elements(*TEN_SAN_PHAM) if e.text]


def cuon(driver, huong="down", percent=0.7):
    """
    Cuộn 1 lần bằng mobile: scrollGesture trên vùng giữa màn hình.
    huong: "down" hoặc "up". Trả về True nếu còn cuộn được, False nếu đã chạm đầu/đáy.
    """
    w = driver.get_window_size()
    return driver.execute_script("mobile: scrollGesture", {
        "left": int(w["width"] * 0.1),
        "top": int(w["height"] * 0.25),
        "width": int(w["width"] * 0.8),
        "height": int(w["height"] * 0.5),
        "direction": huong,
        "percent": percent,
    })


def cuon_xuong(driver, percent=0.7):
    return cuon(driver, "down", percent)


def cuon_len_dau(driver):
    """Đưa danh sách về đầu trang (vì no_reset=True nên app giữ vị trí cuộn của test trước)."""
    for _ in range(20):
        if not cuon(driver, "up", 1.0):
            break


def test_cuon_bang_uiscrollable(man_products):
    """Cuộn tới sản phẩm cuối bằng UiScrollable (UiAutomator)."""
    driver = man_products
    selector = (
        'new UiScrollable(new UiSelector().scrollable(true))'
        f'.scrollIntoView(new UiSelector().text("{SP_CUOI}"))'
    )
    sp = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, selector)
    assert sp.is_displayed()
    assert sp.text == SP_CUOI


def test_cuon_bang_scroll_gesture(man_products):
    """Cuộn xuống bằng mobile: scrollGesture tới khi hết danh sách."""
    driver = man_products
    assert SP_DAU in ten_dang_hien(driver), "Đầu trang phải thấy sản phẩm đầu tiên"

    so_lan = 0
    while cuon_xuong(driver) and so_lan < 20:   # chặn lặp vô hạn
        so_lan += 1

    assert so_lan > 0, "Danh sách không cuộn được"
    assert SP_CUOI in ten_dang_hien(driver), "Cuối trang phải thấy sản phẩm cuối cùng"


def test_gom_tat_ca_san_pham(man_products):
    """Vừa cuộn vừa gom tên sản phẩm, kiểm tra đủ đầu/cuối và không trùng."""
    driver = man_products
    da_thay = []

    for _ in range(20):
        for ten in ten_dang_hien(driver):
            if ten not in da_thay:
                da_thay.append(ten)
        if not cuon_xuong(driver):
            break
    for ten in ten_dang_hien(driver):           # lần cuối khi đã chạm đáy
        if ten not in da_thay:
            da_thay.append(ten)

    assert SP_DAU in da_thay and SP_CUOI in da_thay
    assert len(da_thay) == len(set(da_thay))
    assert len(da_thay) == 6, f"App có 6 sản phẩm, gom được {len(da_thay)}: {da_thay}"


def test_chup_man_hinh_truoc_sau_khi_cuon(man_products):
    """save_screenshot: chụp đầu danh sách và cuối danh sách."""
    driver = man_products
    anh_dau = os.path.join(THU_MUC_ANH, "app3_products_dau.png")
    anh_cuoi = os.path.join(THU_MUC_ANH, "app3_products_cuoi.png")

    assert driver.save_screenshot(anh_dau)
    while cuon_xuong(driver):
        pass
    assert driver.save_screenshot(anh_cuoi)

    for duong_dan in (anh_dau, anh_cuoi):
        assert os.path.exists(duong_dan) and os.path.getsize(duong_dan) > 0


def test_chup_rieng_mot_phan_tu(man_products):
    """element.screenshot: chụp riêng tên sản phẩm đầu tiên."""
    driver = man_products
    sp_dau = driver.find_element(*TEN_SAN_PHAM)
    duong_dan = os.path.join(THU_MUC_ANH, "app3_ten_san_pham_dau.png")

    assert sp_dau.screenshot(duong_dan)
    assert os.path.exists(duong_dan) and os.path.getsize(duong_dan) > 0
    assert sp_dau.text == SP_DAU