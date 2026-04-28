import os
import json
import requests
from datetime import datetime, timedelta

def fetch_github_trending():
    # 使用 GitHub Search API 获取最近 7 天内创建且 Star 最多的项目
    date_threshold = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    query = f"created:>{date_threshold}"
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    items = response.json().get('items', [])[:20] # 取前 20 个
    
    trending_data = []
    for item in items:
        trending_data.append({
            "id": item["id"],
            "name": item["name"],
            "full_name": item["full_name"],
            "description": item["description"],
            "stars": item["stargazers_count"],
            "language": item["language"],
            "html_url": item["html_url"]
        })
        
    return trending_data

def send_pushplus(token, title, content):
    url = "http://www.pushplus.plus/send"
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": "markdown"
    }
    requests.post(url, json=data)

if __name__ == "__main__":
    print("Fetching GitHub trending data...")
    trending_data = fetch_github_trending()
    
    # 写入 JSON 文件，供小程序通过 jsdelivr CDN 访问
    with open('trending.json', 'w', encoding='utf-8') as f:
        json.dump(trending_data, f, ensure_ascii=False, indent=2)
    print("Saved to trending.json")
    
    # 获取环境变量中的 PushPlus Token 并发送推送
    pushplus_token = os.environ.get("PUSHPLUS_TOKEN")
    if pushplus_token and trending_data:
        print("Sending PushPlus notification...")
        top_projects = trending_data[:5]
        content = "### 今日 GitHub 飙升榜 Top 5\n\n"
        for idx, p in enumerate(top_projects, 1):
            content += f"{idx}. **[{p['name']}]({p['html_url']})** (⭐ {p['stars']})\n"
            content += f"   > {p['description'] or '暂无描述'}\n\n"
            
        send_pushplus(pushplus_token, "🔥 今日 GitHub 热门项目速递", content)
        print("Push sent!")
    else:
        print("No PushPlus token found, skipping notification.")
