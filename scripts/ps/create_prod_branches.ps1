git checkout main
git pull origin main

$branches = @("prodab", "prodcd", "prodef", "prodgh", "prodij", "prodkl", "prodmn", "prodop", "prodqr", "prodst", "produv", "prodwx")

# 各ブランチを作成してmainの内容を反映させ、リモートにプッシュ
foreach ($branch in $branches) {
    git checkout -b $branch

    git push origin $branch

    git checkout main

    git branch -d $branch
}

Write-Host "すべてのブランチが作成され、リモートにプッシュされました。"
