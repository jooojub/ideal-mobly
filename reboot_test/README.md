# Mobly Reboot Test

이 디렉토리는 안드로이드 디바이스의 재부팅 및 주요 부팅 단계(`zygote`, `ueventd`, `bootanim`)의 시간 측정 테스트를 수행하기 위한 Mobly 스크립트를 포함하고 있습니다.

## 사전 준비 사항

1.  **Python 3.x** 설치
2.  **Mobly** 설치:
    ```bash
    pip install mobly
    ```
3.  **ADB** 설치 및 경로 설정

## 설정 (Configuration)

`config.yaml` 파일을 열어 테스트할 디바이스의 시리얼 번호를 입력하세요.

```yaml
TestBeds:
  - Name: RebootTestBed
    Controllers:
      AndroidDevice:
        - serial: "여기에_디바이스_시리얼_입력"
```

## 실행 방법

터미널에서 다음 명령어를 실행하여 테스트를 시작합니다.

```bash
python3 reboot_test.py -c config.yaml
```

## 테스트 시나리오

1.  디바이스를 재부팅합니다.
2.  부팅이 완료될 때까지 대기합니다.
3.  다음 프로퍼티 값을 획득하여 나노초(ns) 단위로 출력합니다.
    *   `ro.boottime.zygote` (또는 `ro.boottime.zygote64`)
    *   `ro.boottime.ueventd` (udeved)
    *   `ro.boottime.bootanim`
4.  위 과정을 10회 반복합니다.
5.  테스트 완료 후 각 항목별 최소(Min), 최대(Max), 평균(Avg) 값을 출력합니다.