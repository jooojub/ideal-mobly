import time
from mobly import base_test
from mobly import test_runner
from mobly.controllers import android_device
from mobly import asserts

class CheckSystemSoundsTest(base_test.BaseTestClass):

    def setup_class(self):
        # AndroidDevice 컨트롤러 등록
        self.ads = self.register_controller(android_device)
        self.dut = self.ads[0]
        
        # UI Automator 제어를 위해 Mobly Bundled Snippets 로드
        # (사전에 adb install로 해당 apk가 설치되어 있어야 함)
        self.dut.load_snippet('mbs', 'com.google.android.mobly.snippet.bundled')

    def test_check_system_sounds_scenario(self):
        """
        요청된 시나리오:
        1. 보드 재부팅 -> 2. 1분 대기 -> 3. Quick Settings 클릭 -> 4. 2초 대기
        -> 5. Settings 클릭 -> 6. 2초 대기 -> 7. System 스크롤 및 클릭 -> 8. 2초 대기
        -> 9. switch_widget 스크롤 및 확인 -> 10. Pass/Fail 판정
        """
        
        # 1. 보드 재부팅
        self.dut.reboot()
        
        # 2. 1분 대기
        time.sleep(60)

        # 3. content-desc="Open quick settings panel" UI 찾은 후 클릭
        self.dut.mbs.clickByDesc("Open quick settings panel")

        # 4. 2초 대기
        time.sleep(2)

        # 5. content-desc="Open Settings" UI 찾은 후 클릭
        self.dut.mbs.clickByDesc("Open Settings")

        # 6. 2초 대기
        time.sleep(2)

        # 7. Text="System" 나올때 까지 스크롤 후 ui 찾으면 클릭
        # 설정 메뉴는 스크롤이 필요할 수 있으므로 scrollable=True인 컨테이너에서 검색
        self.dut.mbs.scrollToText("System")
        self.dut.mbs.clickByText("System")

        # 8. 2초 대기
        time.sleep(2)

        # 9. resource-id="android:id/switch_widget" 이 나올 때 까지 스크롤 후 checked 확인
        # System 메뉴 내부에서도 스크롤이 필요할 수 있음
        self.dut.mbs.scrollToId("android:id/switch_widget")
        
        # 해당 UI의 정보 가져오기 (새로 추가한 RPC 사용)
        is_checked = self.dut.mbs.isCheckedById("android:id/switch_widget")

        # 10. checked가 true이면 Pass 아니면 Fail
        asserts.assert_true(is_checked, 
                            f"Test Failed: Switch widget is not checked. (Current state: {is_checked})")

if __name__ == '__main__':
    test_runner.main()