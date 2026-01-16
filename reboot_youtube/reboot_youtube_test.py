import base64
import os
import time

from mobly import base_test
from mobly import test_runner
from mobly.controllers import android_device

class RebootYoutubeTest(base_test.BaseTestClass):

  def setup_class(self):
    # Android 장치 등록
    self.dut = self.register_controller(android_device)[0]
    
    # 참조 이미지 로드 (테스트 실행 경로 또는 filesdir에 ref_image.png가 있어야 함)
    image_filename = 'ref_image.png'
    image_path = os.path.join(self.user_params.get('filesdir', '.'), image_filename)
    
    if os.path.exists(image_path):
      with open(image_path, 'rb') as f:
        self.ref_image_b64 = base64.b64encode(f.read()).decode('utf-8')
      self.dut.log.info(f"Loaded reference image from {image_path}")
    else:
      self.dut.log.warning(f"Reference image not found at {image_path}. Test may fail.")
      self.ref_image_b64 = ""

  def test_reboot_and_match_image(self):
    durations = []
    
    for i in range(1, 11):
      self.dut.log.info(f'--- Iteration {i}/10 start ---')
      
      try:
        # 1. 재 부팅
        self.dut.log.info('Rebooting device...')
        self.dut.reboot()
        
        # 1. 재 부팅 후 1분 대기
        self.dut.log.info('Reboot complete. Waiting for 60 seconds...')
        time.sleep(60)
        
        # Snippet 로드 (Reboot 시 연결이 끊기므로 매번 다시 로드해야 함)
        self.dut.load_snippet('mbs', 'com.google.android.mobly.snippet.bundled')

        # 2. 192, 982 위치를 click
        self.dut.log.info('Clicking at 192, 982')
        # 클릭 직전 시간 측정 시작
        start_time = time.time()
        self.dut.adb.shell(['input', 'tap', '192', '982'])

        # 3. 130 x 130 사이즈의 ref 이미지가 120, 130 위치에 나올 때 까지 wait, timeout은 10초
        self.dut.log.info('Waiting for image match...')
        self.dut.mbs.waitForImageMatching(
            self.ref_image_b64,
            120,   # x
            130,   # y
            130,   # width
            130,   # height
            10000  # timeout 10s
        )
        
        # 4. 매칭이 되면 click 한 시점 이후 image가 나왔을 때 까지의 시간을 측정
        end_time = time.time()
        duration = end_time - start_time
        durations.append(duration)
        self.dut.log.info(f'Iteration {i}: Match took {duration:.4f} seconds')

      except Exception as e:
        self.dut.log.error(f'Iteration {i} failed: {e}')
      
      finally:
        # 다음 반복을 위해 스니펫 언로드
        if hasattr(self.dut, 'mbs'):
          self.dut.unload_snippet('mbs')

    # 6. min / max / avg 출력
    if durations:
      min_time = min(durations)
      max_time = max(durations)
      avg_time = sum(durations) / len(durations)
      
      result_msg = (
          f'\n{"="*40}\n'
          f'Test Results (10 iterations)\n'
          f'Min: {min_time:.4f}s\n'
          f'Max: {max_time:.4f}s\n'
          f'Avg: {avg_time:.4f}s\n'
          f'{"="*40}'
      )
      self.dut.log.info(result_msg)
    else:
      self.dut.log.error('No successful iterations to calculate statistics.')

if __name__ == '__main__':
  test_runner.main()