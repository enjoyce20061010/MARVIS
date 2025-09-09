# 開發者貢獻指南

## 分支策略
- main：受保護，禁止直接推送，僅允許透過 PR 合併
- dev（可選）：日常整合分支
- feature/*、fix/*：以議題為單位開分支

## PR 規範
- 每個 PR 必須對應 Issue，並附上：
  - 變更摘要、風險、是否影響設定/API
  - 測試結果（包含 coverage 摘要）
- 至少 1 位 reviewer（可自審）
- CI 全綠（mypy、ruff、black、pytest、coverage）才可合併

## 本地開發
- 建立虛擬環境並安裝依賴：
  ```bash
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  pip install pytest pytest-cov ruff black mypy pre-commit
  ```
- 格式與規則檢查：
  ```bash
  black --check .
  ruff check .
  mypy .
  pytest -q --cov=. --cov-report=term-missing
  ```
- 建議啟用 pre-commit：
  ```bash
  pre-commit install
  ```

## 型別、Lint 與測試
- 公開 API 與關鍵資料結構必須有型別註記，mypy . 必須 0 錯誤
- 以 black 統一格式、ruff 檢查規則
- 覆蓋率基線（建議 ≥70%），關鍵模組優先補測

## 祕密管理
- 使用 .env 或環境變數設定 OPENAI_API_KEY，禁止將金鑰寫入程式碼或日誌
