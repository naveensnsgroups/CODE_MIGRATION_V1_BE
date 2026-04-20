import re
import os

# Files to clean
files = [
    r'e:\CODE_MIGRATION_V1\CODE_MIGRATION_V1_FE\src\features\ingestion\hooks\UseIngestion.ts',
    r'e:\CODE_MIGRATION_V1\CODE_MIGRATION_V1_FE\src\features\ingestion\components\Workbench.tsx',
    r'e:\CODE_MIGRATION_V1\CODE_MIGRATION_V1_FE\src\features\ingestion\components\RepoSelector.tsx',
    r'e:\CODE_MIGRATION_V1\CODE_MIGRATION_V1_FE\src\features\ingestion\components\modals\PrivateRepoModal.tsx',
    r'e:\CODE_MIGRATION_V1\CODE_MIGRATION_V1_FE\src\features\ingestion\components\dashboard\StrategyHero.tsx',
    r'e:\CODE_MIGRATION_V1\CODE_MIGRATION_V1_FE\src\features\ingestion\components\dashboard\RoutesHero.tsx',
    r'e:\CODE_MIGRATION_V1\CODE_MIGRATION_V1_FE\src\features\ingestion\components\dashboard\ReportDashboard.tsx',
    r'e:\CODE_MIGRATION_V1\CODE_MIGRATION_V1_FE\src\features\ingestion\components\dashboard\LogicHero.tsx',
    r'e:\CODE_MIGRATION_V1\CODE_MIGRATION_V1_FE\src\features\ingestion\components\AnalysisReport.tsx',
    r'e:\CODE_MIGRATION_V1\CODE_MIGRATION_V1_FE\src\api\AnalysisClient.ts',
    r'e:\CODE_MIGRATION_V1\CODE_MIGRATION_V1_BE\app\services\email_service.py',
    r'e:\CODE_MIGRATION_V1\CODE_MIGRATION_V1_BE\app\services\clone_service.py',
    r'e:\CODE_MIGRATION_V1\CODE_MIGRATION_V1_BE\app\api\endpoints\ingest.py',
    r'e:\CODE_MIGRATION_V1\CODE_MIGRATION_V1_BE\app\api\endpoints\analysis.py',
]

# Broad emoji + symbol unicode ranges
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F000-\U0001F02F"
    "\U0001F0A0-\U0001F0FF"
    "\U0001F100-\U0001F1FF"
    "\U0001F200-\U0001F2FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "]+",
    flags=re.UNICODE
)

for path in files:
    if not os.path.exists(path):
        print(f"  SKIP (not found): {path}")
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    cleaned = EMOJI_PATTERN.sub('', content)
    
    if cleaned != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f"  CLEANED: {os.path.basename(path)}")
    else:
        print(f"  NO CHANGE: {os.path.basename(path)}")

print("\nDone. All emoji removed from code files.")
