import subprocess
from datetime import datetime

# 1. 변경 파일 모두 add
subprocess.run(["git", "add", "."])

# 2. 커밋 메시지에 현재 시각 포함
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
commit_msg = f"자동 커밋: {now}"
subprocess.run(["git", "commit", "-m", commit_msg])

# 3. 원격 저장소로 push
subprocess.run(["git", "push", "origin", "main"])

print("모든 변경사항이 GitHub에 푸시되었습니다.")
