import sys
import time
from mobly import base_test
from mobly import test_runner
from mobly.controllers import android_device

class RebootTest(base_test.BaseTestClass):
    def setup_class(self):
        # AndroidDevice 컨트롤러 등록
        self.ads = self.register_controller(android_device)
        self.dut = self.ads[0]

    def test_reboot_scenario(self):
        results = []
        iteration_count = 10

        for i in range(1, iteration_count + 1):
            self.dut.log.info(f"=== Reboot Iteration {i}/{iteration_count} ===")
            
            # 1. 보드 재부팅
            # dut.reboot()는 adb 연결이 다시 될 때까지 대기합니다.
            self.dut.reboot()
            
            # 2. property에 ro.boottime.sys.boot_completed 이 나올 때 까지 대기 및 값 획득
            prop_value = None
            timeout = 60 # seconds
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # getprop 명령어로 값 읽기
                val = self.dut.adb.shell(['getprop', 'ro.boottime.sys.boot_completed']).strip()
                if val:
                    prop_value = val
                    break
                time.sleep(1)
            
            if not prop_value:
                raise TimeoutError(f"Iteration {i}: Failed to get ro.boottime.sys.boot_completed within {timeout}s")

            # 3. nano sec 단위로 변환 후 출력
            try:
                # ro.boottime.sys.boot_completed 값은 이미 ns 단위입니다.
                val_ns = int(prop_value)
                
                self.dut.log.info(f"Iteration {i} Result: {val_ns} ns (Raw: {prop_value})")
                results.append(val_ns)
            except ValueError:
                self.dut.log.error(f"Iteration {i}: Invalid property value '{prop_value}'")
                continue

        # 5. min / max / avg 값 출력
        if results:
            min_val = min(results)
            max_val = max(results)
            avg_val = sum(results) / len(results)
            
            self.dut.log.info("=== Final Statistics ===")
            self.dut.log.info(f"Min: {min_val} ns")
            self.dut.log.info(f"Max: {max_val} ns")
            self.dut.log.info(f"Avg: {avg_val:.2f} ns")
        else:
            # 결과가 하나도 없으면 테스트 실패 처리
            assert False, "No valid measurements collected."

if __name__ == '__main__':
    test_runner.main()