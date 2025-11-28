import arxiv
import json
import os
import random
import datetime
import time
from openai import OpenAI

# 1. 配置
TARGET_CATEGORIES = ["cs.AI", "cs.CL", "cs.LG", "cs.CV"]
JSON_FILE = "papers_data.json"
API_KEY = os.environ.get("DEEPSEEK_API_KEY") # 从环境变量获取 Key
BASE_URL = "https://api.deepseek.com"

# 颜色池
GRADIENTS = [
    "bg-gradient-to-br from-indigo-600 to-blue-600",
    "bg-gradient-to-br from-purple-500 to-pink-600",
    "bg-gradient-to-br from-orange-400 to-red-500",
    "bg-gradient-to-br from-emerald-500 to-teal-600",
    "bg-gradient-to-br from-slate-700 to-slate-900",
    "bg-gradient-to-br from-rose-500 to-red-600",
]

if not API_KEY:
    raise ValueError("未检测到 DEEPSEEK_API_KEY 环境变量！")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def get_existing_papers():
    """读取已有的 JSON 数据"""
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def fetch_arxiv_updates(existing_ids):
    """抓取 ArXiv 新论文"""
    print("🚀 正在连接 ArXiv...")
    query = " OR ".join([f"cat:{cat}" for cat in TARGET_CATEGORIES])
    
    # 搜索最近 100 篇
    search = arxiv.Search(
        query=query,
        max_results=100, 
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    
    client_arxiv = arxiv.Client(page_size=100, delay_seconds=3, num_retries=3)
    new_papers = []
    
    # 设置时间窗口：过去 25 小时 (GitHub Action 每天运行一次，稍微多抓一点防止漏掉)
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    time_threshold = utc_now - datetime.timedelta(hours=25)

    for r in client_arxiv.results(search):
        paper_id = r.entry_id.split('/')[-1]
        
        # 1. 如果论文太旧，停止处理 (因为是按时间倒序的)
        if r.updated < time_threshold:
            break
            
        # 2. 如果 ID 已存在，跳过
        if paper_id in existing_ids:
            continue
            
        # 3. 再次确认分类 (ArXiv 搜索有时不精准)
        cats = [c for c in r.categories if c in TARGET_CATEGORIES]
        if not cats:
            continue

        new_papers.append(r)

    print(f"🔍 发现 {len(new_papers)} 篇新论文需要处理。")
    return new_papers

def ai_process(title, abstract):
    """调用 DeepSeek 进行总结和翻译"""
    prompt = f"""
    请处理以下论文信息：
    Title: {title}
    Abstract: {abstract}

    任务：
    1. Innovation: 用中文一句话总结核心创新点（<50字）。
    2. Abstract_zh: 将摘要翻译成中文。

    请仅返回合法的 JSON 格式：
    {{ "innovation": "...", "abstract_zh": "..." }}
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a JSON generator."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}, # 强制 JSON 模式
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"⚠️ AI 处理出错: {e}")
        return {"innovation": "AI 总结暂不可用", "abstract_zh": "翻译暂不可用"}

# 将 daily_fetch.py 中的 main 函数替换为这个：

def main():
    existing_data = get_existing_papers()
    existing_ids = {p['id'] for p in existing_data}
    
    # 尝试获取新数据
    try:
        raw_papers = fetch_arxiv_updates(existing_ids)
    except Exception as e:
        print(f"❌ 获取 ArXiv 数据出错: {e}")
        raw_papers = []

    processed_list = []
    
    # 如果有新论文，进行处理
    if raw_papers:
        for i, r in enumerate(raw_papers):
            print(f"[{i+1}/{len(raw_papers)}] 处理中: {r.title[:30]}...")
            
            ai_res = ai_process(r.title, r.summary)
            
            paper_obj = {
                "id": r.entry_id.split('/')[-1],
                "orig_title": r.title.replace('\n', ' '),
                "tags": [t.split('.')[-1] for t in r.categories if t in TARGET_CATEGORIES],
                "userTags": [],
                "coverGradient": random.choice(GRADIENTS),
                "summary": { "innovation": ai_res.get("innovation", "无总结") },
                "abstract_zh": ai_res.get("abstract_zh", "无翻译"),
                "abstract_en": r.summary.replace('\n', ' '),
                "authors": [a.name for a in r.authors[:5]],
                "affiliation": r.categories[0], 
                "date": r.updated.strftime("%Y-%m-%d"),
                "pdf_url": r.pdf_url,
                "likes": 0, "isLiked": False, 
                "collections": 0, "isCollected": False,
                "comments": [], "qa": [],
                "expanded": False, "isTranslated": False
            }
            processed_list.append(paper_obj)
            time.sleep(1) # 避免触发 API 速率限制
    else:
        print("⚠️ 本次没有发现新论文。")

    # --- 关键修改：无论有没有新论文，都执行合并与保存 ---
    
    # 合并：新论文放最前面
    final_data = processed_list + existing_data
    
    # 强制保存（如果文件不存在，这里会创建它；如果存在，会更新它）
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 数据处理完成。文件已保存至 {JSON_FILE} (当前总数: {len(final_data)})")
    
    print(f"💾 更新完成，新增 {len(processed_list)} 篇。")

if __name__ == "__main__":
    main()
