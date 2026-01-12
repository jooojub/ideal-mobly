# Mobly App Launch Test

이 디렉토리는 안드로이드 디바이스를 재부팅한 후 YouTube 앱을 실행하여 실행 시간을 측정하는 Mobly 테스트를 포함합니다.

## 사전 준비 사항

1.  **Mobly 설치**:
    ```bash
    pip install mobly
    ```
2.  **Snippet APK 설치**:
    `UiControlSnippet`이 포함된 `mobly-bundled-snippets` APK가 테스트 대상 디바이스에 설치되어 있어야 합니다.
    ```bash
    adb install -r -g <path_to_mobly_bundled_snippets_apk>
    ```
3.  **Config 설정**:
    `config.yaml` 파일의 `serial` 필드에 테스트할 디바이스의 시리얼 번호를 입력하세요.

## 테스트 시나리오

1.  디바이스를 재부팅합니다.
2.  시스템 안정화를 위해 2분간 대기합니다.
3.  `UiControlSnippet`을 사용하여 다음 동작을 수행합니다:
    *   ClassName: `android.widget.TextView`, Text: `Apps` 인 요소를 클릭 (앱 서랍 진입)
    *   Content-Desc: `YouTube` 인 요소를 클릭 (앱 실행)
4.  Logcat의 `ActivityTaskManager: Displayed` 로그를 분석하여 앱 실행 시간(Launch Time)을 측정합니다.
5.  위 과정을 10회 반복합니다.
6.  최소(Min), 최대(Max), 평균(Avg) 실행 시간을 출력합니다.

## 실행 방법

터미널에서 다음 명령어를 실행합니다:

```bash
python3 launch_app_test.py -c config.yaml
```

> **참고**: 테스트 중 디바이스가 재부팅되므로, USB 연결이 안정적인지 확인해주세요.