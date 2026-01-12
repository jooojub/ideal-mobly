import re
import time
from mobly import base_test
from mobly import test_runner
from mobly.controllers import android_device
from mobly.controllers.android_device_lib import jsonrpc_client_base

class LaunchAppTest(base_test.BaseTestClass):
    def setup_class(self):
        # AndroidDevice 컨트롤러 등록
        self.ads = self.register_controller(android_device)
        self.dut = self.ads[0]
        # UiControlSnippet 로드 (패키지명은 빌드 설정에 따라 다를 수 있으나 기본값 사용)
        self.dut.load_snippet('mbs', 'com.google.android.mobly.snippet.bundled')

    def test_youtube_launch_scenario(self):
        iteration_count = 10
        results = []

        for i in range(1, iteration_count + 1):
            self.dut.log.info(f"=== Iteration {i}/{iteration_count} ===")

            # 1. 재부팅
            self.dut.log.info("Rebooting device...")
            self.dut.reboot()
            
            # 2. 2분 대기
            self.dut.log.info("Waiting for 2 minutes after reboot...")
            time.sleep(120)

            # 화면 켜기 및 잠금 해제 (테스트 안정성을 위해 추가)
            self.dut.adb.shell(['input', 'keyevent', 'KEYCODE_WAKEUP'])
            self.dut.adb.shell(['wm', 'dismiss-keyguard'])
            time.sleep(2)

            # Logcat 버퍼 비우기 (측정 정확도를 위해)
            self.dut.adb.shell(['logcat', '-c'])

            try:
                # 2. class Name: "android.widget.TextView" 의 text="Apps" 를 click
                # (앱 서랍 진입)
                self.dut.log.info("Clicking 'Apps'...")
                self.dut.mbs.clickByClassNameAndText("android.widget.TextView", "Apps")
                time.sleep(3) # UI 애니메이션 대기

                # 3. content-desc: "YouTube"를 클릭
                self.dut.log.info("Clicking 'YouTube'...")
                self.dut.mbs.clickByDesc("YouTube")
                
                # 4. YouTube 클릭 후 화면에 나오기 까지의 시간을 logcat 기준으로 측정
                launch_time = self._measure_launch_time()
                
                if launch_time is not None:
                    self.dut.log.info(f"Iteration {i} Result: {launch_time} ms")
                    results.append(launch_time)
                else:
                    self.dut.log.error(f"Iteration {i}: Failed to measure launch time (Log pattern not found).")

            except jsonrpc_client_base.ApiError as e:
                self.dut.log.error(f"Iteration {i}: UI interaction failed - {e}")
            except Exception as e:
                self.dut.log.error(f"Iteration {i}: Unexpected error - {e}")

        # 5. 통계 출력
        if results:
            min_val = min(results)
            max_val = max(results)
            avg_val = sum(results) / len(results)
            self.dut.log.info("=== Final Statistics ===")
            self.dut.log.info(f"Min: {min_val} ms")
            self.dut.log.info(f"Max: {max_val} ms")
            self.dut.log.info(f"Avg: {avg_val:.2f} ms")
        else:
            assert False, "No valid measurements collected."

    def _measure_launch_time(self):
        # 시스템 로그에서 앱 실행 시간 파싱
        # 예: ActivityTaskManager: Displayed com.google.android.youtube/...: +1s234ms
        timeout = 20 # 최대 20초 대기
        start_wait = time.time()
        
        # 정규식: Displayed [패키지명]...: +[시간]
        pattern = re.compile(r"Displayed com\.google\.android\.youtube.*:\s+\+([0-9sms]+)")
        
        while time.time() - start_wait < timeout:
            # logcat 덤프 (최근 로그 확인)
            logs = self.dut.adb.shell(['logcat', '-d', '-b', 'system', '-b', 'main', '-s', 'ActivityTaskManager']).decode('utf-8')
            
            # 로그 라인 역순 검색 (최신 로그 우선)
            for line in reversed(logs.splitlines()):
                match = pattern.search(line)
                if match:
                    duration_str = match.group(1)
                    return self._parse_duration(duration_str)
            
            time.sleep(1)
        
        return None

    def _parse_duration(self, duration_str):
        # 포맷 예시: "1s234ms", "500ms"
        total_ms = 0
        try:
            if 's' in duration_str:
                parts = duration_str.split('s')
                sec = int(parts[0])
                ms = int(parts[1].replace('ms', '')) if 'ms' in parts[1] else 0
                total_ms = sec * 1000 + ms
            elif 'ms' in duration_str:
                total_ms = int(duration_str.replace('ms', ''))
        except ValueError:
            return None
        return total_ms

if __name__ == '__main__':
    test_runner.main()