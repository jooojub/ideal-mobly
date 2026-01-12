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
        # 측정할 타겟 속성 정의 (요청된 zygote, udeved(ueventd로 간주), bootanim)
        target_props = {
            'ueventd': 'ro.boottime.ueventd',
            'zygote': 'ro.boottime.zygote',
            'bootanim': 'ro.boottime.bootanim'
        }

        # 결과 저장을 위한 딕셔너리 초기화
        results = {key: [] for key in target_props.keys()}
        iteration_count = 10

        for i in range(1, iteration_count + 1):
            self.dut.log.info(f"=== Reboot Iteration {i}/{iteration_count} ===")
            
            # 1. 보드 재부팅
            self.dut.reboot()
            # 부팅 완료 대기 (프로퍼티가 확실히 생성되도록 대기)
            self.dut.wait_for_boot_completion()
            
            # 2. 각 타겟별 시간 측정
            for name, prop_key in target_props.items():
                val = self.dut.adb.shell(['getprop', prop_key]).strip()

                # zygote가 비어있으면 zygote64 시도 (64비트 시스템 대응)
                if name == 'zygote' and not val:
                    val = self.dut.adb.shell(['getprop', 'ro.boottime.zygote64']).strip()

                if val:
                    try:
                        # 3. milli sec 단위로 변환 후 출력 (ro.boottime.* 값은 일반적으로 이미 ns 단위임)
                        val_ms = int(val) // 1000000
                        self.dut.log.info(f"Iteration {i} [{name}]: {val_ms} ms")
                        results[name].append(val_ms)
                    except ValueError:
                        self.dut.log.error(f"Iteration {i} [{name}]: Invalid value '{val}'")
                else:
                    self.dut.log.error(f"Iteration {i} [{name}]: Failed to get property")

        # 5. min / max / avg 값 출력
        self.dut.log.info("=== Final Statistics ===")
        for name, values in results.items():
            if values:
                min_val = min(values)
                max_val = max(values)
                avg_val = sum(values) / len(values)
                self.dut.log.info(f"[{name}] Min: {min_val} ms, Max: {max_val} ms, Avg: {avg_val:.2f} ms")
            else:
                self.dut.log.error(f"[{name}] No valid measurements collected.")

if __name__ == '__main__':
    test_runner.main()