#!/usr/bin/env python3
"""
Bug Dashboard 构建器。

工作流:
1. 拉 Jira 当前 assignee=liusiyi 未关闭的 bug
2. 合并 diagnoses.json 里我维护的诊断
3. 渲染 index.html(单文件,内嵌数据,浏览器直接打开)

使用:
    python3 build.py            # 全量重建
    python3 build.py --jql "..."  # 自定义 JQL

诊断添加:在 diagnoses.json 里加 key+对象即可,字段见文件 _schema 注释。
"""
import json, subprocess, sys, os, html, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
JIRA_AUTH = Path.home() / ".git-jira-commit-assist-auth.json"
DIAGNOSES_FILE = ROOT / "diagnoses.json"
OUTPUT_HTML = ROOT / "index.html"
DEFAULT_JQL = "assignee=liusiyi AND issuetype=Bug AND resolution=Unresolved ORDER BY updated DESC"

def fetch_jira(jql=DEFAULT_JQL):
    auth = json.loads(JIRA_AUTH.read_text())
    url = f"{auth['baseUrl']}/rest/api/2/search"
    params = f"jql={urllib.request.quote(jql)}&fields=summary,description,status,priority,project,created,updated&maxResults=200"
    req = urllib.request.Request(
        f"{url}?{params}",
        headers={"Authorization": f"Bearer {auth['token']}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def auto_module(summary, project_key):
    """根据 summary 关键词自动分组。诊断文件里的 module 字段优先。"""
    s = summary
    if project_key.startswith("P2"):
        if "新套装" in s: return "5月节日-新套装(巨龙套)"
        if "头像框礼包" in s: return "5月节日-头像框礼包"
        if "线上问题" in s: return "线上问题"
        if "5月节日" in s or "拓荒" in s: return "5月节日-其他"
        return "其他"
    if project_key.startswith("X2"):
        if "节日累充" in s: return "X2-节日累充"
        if "英雄累充" in s: return "X2-英雄累充"
        if "巨猿" in s: return "X2-巨猿活动"
        return "X2-其他"
    return "其他"

def merge(jira_data, diagnoses, jira_base):
    bugs = []
    for issue in jira_data.get("issues", []):
        key = issue["key"]
        f = issue["fields"]
        diag = diagnoses.get(key, {})
        proj = f.get("project", {}).get("key", "")
        bugs.append({
            "key": key,
            "summary": f.get("summary", ""),
            "description": f.get("description") or "",
            "status": f.get("status", {}).get("name", ""),
            "priority": f.get("priority", {}).get("name", "") if f.get("priority") else "",
            "project": proj,
            "created": (f.get("created") or "")[:10],
            "updated": (f.get("updated") or "")[:10],
            "url": f"{jira_base}/browse/{key}",
            "module": diag.get("module") or auto_module(f.get("summary",""), proj),
            "category": diag.get("category", ""),
            "cause": diag.get("cause", ""),
            "config_tables": diag.get("config_tables", []),
            "suggestion": diag.get("suggestion", ""),
            "diagnosed_at": diag.get("diagnosed_at", ""),
            "diagnosed": key in diagnoses,
        })
    return bugs

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>Bug Dashboard - liusiyi</title>
<style>
*{box-sizing:border-box}
body{margin:0;font:14px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;color:#2c3e50;background:#f5f7fa}
.layout{display:flex;height:100vh}
.sidebar{width:340px;background:#fff;border-right:1px solid #e1e8ed;display:flex;flex-direction:column}
.search{padding:10px;border-bottom:1px solid #e1e8ed}
.search input{width:100%;padding:8px 10px;border:1px solid #d0d7de;border-radius:4px;font-size:13px;outline:none}
.search input:focus{border-color:#1976d2}
.stats{padding:8px 12px;font-size:11px;color:#666;background:#fafbfc;border-bottom:1px solid #e1e8ed}
.groups{flex:1;overflow-y:auto;padding:4px 0}
.group-header{padding:8px 12px;background:#f0f4f8;font-weight:600;font-size:12px;color:#1f2937;cursor:pointer;user-select:none;display:flex;justify-content:space-between;align-items:center}
.group-header:hover{background:#e7eef5}
.group-count{background:#cfd8dc;color:#37474f;padding:1px 7px;border-radius:10px;font-size:10px;font-weight:500}
.subgroup{margin:2px 0}
.subgroup-header{padding:5px 12px 5px 24px;font-size:12px;color:#546e7a;cursor:pointer;user-select:none;display:flex;justify-content:space-between;align-items:center}
.subgroup-header:hover{background:#f5f8fb;color:#1976d2}
.subgroup-count{color:#90a4ae;font-size:10px}
.bug-item{padding:6px 12px 6px 32px;cursor:pointer;border-left:3px solid transparent;font-size:12px}
.bug-item:hover{background:#f5f8fb}
.bug-item.active{background:#e3f2fd;border-left-color:#1976d2}
.bug-key{font-family:'SF Mono',Monaco,Consolas,monospace;color:#1976d2;font-size:11px;font-weight:500}
.bug-key-warn{color:#e65100}
.bug-summary{color:#37474f;margin-top:1px;line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.collapsed > div:not(.group-header):not(.subgroup-header){display:none}
.collapsed > .subgroup > .bug-item{display:none}

.main{flex:1;overflow-y:auto;padding:24px 32px;background:#fff}
.empty{color:#90a4ae;font-style:italic;padding:60px 0;text-align:center}
.detail-header{padding-bottom:14px;border-bottom:2px solid #f0f4f8;margin-bottom:20px}
.detail-key{font-family:'SF Mono',Monaco,Consolas,monospace;color:#1976d2;font-size:13px;font-weight:600}
.detail-key a{color:#1976d2;text-decoration:none}
.detail-key a:hover{text-decoration:underline}
.detail-summary{font-size:18px;font-weight:600;color:#1f2937;margin-top:8px;line-height:1.4}
.detail-meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.tag{padding:3px 10px;border-radius:3px;font-size:11px;font-weight:500}
.tag-status{background:#fff3e0;color:#e65100}
.tag-priority{background:#e8eaf6;color:#3f51b5}
.tag-project{background:#e0f2f1;color:#00695c}
.tag-warn{background:#ffebee;color:#c62828}
.tag-cat-localization{background:#e3f2fd;color:#1565c0}
.tag-cat-config{background:#fff3e0;color:#e65100}
.tag-cat-art{background:#fce4ec;color:#ad1457}
.tag-cat-client{background:#f3e5f5;color:#6a1b9a}
.tag-cat-other{background:#eceff1;color:#455a64}

.section{margin:18px 0}
.section h3{font-size:13px;color:#37474f;margin:0 0 8px 0;font-weight:600;letter-spacing:0.3px;text-transform:uppercase}
.cause-box{background:#fff8e1;border-left:4px solid #ffa000;padding:12px 14px;border-radius:0 4px 4px 0;color:#5d4037;line-height:1.7}
.suggest-box{background:#e8f5e9;border-left:4px solid #43a047;padding:12px 14px;border-radius:0 4px 4px 0;color:#1b5e20;line-height:1.7;white-space:pre-wrap}
.tables-box{display:flex;gap:6px;flex-wrap:wrap}
.table-tag{padding:3px 10px;background:#e1f5fe;color:#0277bd;border-radius:3px;font-family:'SF Mono',Monaco,Consolas,monospace;font-size:11px}
.desc-box{background:#fafbfc;padding:12px 14px;border:1px solid #e1e8ed;border-radius:4px;white-space:pre-wrap;color:#37474f;font-size:13px}
.warn-box{background:#fff3e0;border-left:4px solid #ff9800;padding:10px 14px;color:#e65100;border-radius:0 4px 4px 0}

.diagnosed-mark{font-size:10px;color:#43a047;margin-left:4px}
.undiagnosed-mark{font-size:10px;color:#ff9800;margin-left:4px}
.footer{padding:8px 12px;font-size:10px;color:#90a4ae;border-top:1px solid #e1e8ed;background:#fafbfc;text-align:center}
</style>
</head>
<body>
<div class="layout">
  <div class="sidebar">
    <div class="search"><input type="text" id="search" placeholder="搜索 (key/标题/原因)..."></div>
    <div class="stats" id="stats"></div>
    <div class="groups" id="groups"></div>
    <div class="footer">最后更新: __BUILD_TIME__</div>
  </div>
  <div class="main">
    <div id="detail"><div class="empty">← 从左边选一条 bug 查看详情</div></div>
  </div>
</div>
<script>
const BUGS = __BUGS_JSON__;

// 按项目→模块分组
function groupBugs(bugs){
  const projects = {};
  for(const b of bugs){
    const proj = b.project || 'OTHER';
    const mod = b.module || '其他';
    if(!projects[proj]) projects[proj] = {};
    if(!projects[proj][mod]) projects[proj][mod] = [];
    projects[proj][mod].push(b);
  }
  return projects;
}

function escapeHTML(s){
  return (s||'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
}

let currentKey = null;
let filterText = '';

function matchFilter(bug, q){
  if(!q) return true;
  const lower = q.toLowerCase();
  return (bug.key||'').toLowerCase().includes(lower)
      || (bug.summary||'').toLowerCase().includes(lower)
      || (bug.cause||'').toLowerCase().includes(lower)
      || (bug.module||'').toLowerCase().includes(lower);
}

function renderSidebar(){
  const filtered = BUGS.filter(b => matchFilter(b, filterText));
  const grouped = groupBugs(filtered);
  const container = document.getElementById('groups');
  container.innerHTML = '';
  document.getElementById('stats').innerHTML =
    `<b>${filtered.length}</b> bug${filtered.length!==BUGS.length?` (从 ${BUGS.length} 过滤)`:''}` +
    ` · 已诊断 <b>${filtered.filter(b=>b.diagnosed).length}</b>`;

  // 项目按 P2DEV → X2 → 其他 排序
  const projOrder = Object.keys(grouped).sort((a,b)=>{
    const w = k => k.startsWith('P2') ? 0 : k.startsWith('X2') ? 1 : 2;
    return w(a) - w(b);
  });

  for(const proj of projOrder){
    const projDiv = document.createElement('div');
    const totalProj = Object.values(grouped[proj]).reduce((s,arr)=>s+arr.length, 0);
    const header = document.createElement('div');
    header.className = 'group-header';
    header.innerHTML = `<span>${escapeHTML(proj)}</span><span class="group-count">${totalProj}</span>`;
    header.onclick = ()=>projDiv.classList.toggle('collapsed');
    projDiv.appendChild(header);

    // 模块按数量倒序
    const modules = Object.entries(grouped[proj]).sort((a,b)=>b[1].length-a[1].length);
    for(const [mod, bugs] of modules){
      const subDiv = document.createElement('div');
      subDiv.className = 'subgroup';
      const subHeader = document.createElement('div');
      subHeader.className = 'subgroup-header';
      subHeader.innerHTML = `<span>${escapeHTML(mod)}</span><span class="subgroup-count">${bugs.length}</span>`;
      subDiv.appendChild(subHeader);

      for(const b of bugs){
        const item = document.createElement('div');
        item.className = 'bug-item' + (b.key===currentKey ? ' active' : '');
        const mark = b.diagnosed ? '<span class="diagnosed-mark" title="已诊断">●</span>' : '<span class="undiagnosed-mark" title="待诊断">○</span>';
        item.innerHTML = `<div class="bug-key">${escapeHTML(b.key)}${mark}</div>` +
                         `<div class="bug-summary">${escapeHTML(b.summary)}</div>`;
        item.onclick = ()=>{ currentKey = b.key; renderSidebar(); renderDetail(b); };
        subDiv.appendChild(item);
      }
      projDiv.appendChild(subDiv);
    }
    container.appendChild(projDiv);
  }
}

function renderDetail(bug){
  const main = document.getElementById('detail');
  const tags = [];
  if(bug.project) tags.push(`<span class="tag tag-project">${escapeHTML(bug.project)}</span>`);
  if(bug.status) tags.push(`<span class="tag tag-status">${escapeHTML(bug.status)}</span>`);
  if(bug.priority) tags.push(`<span class="tag tag-priority">${escapeHTML(bug.priority)}</span>`);
  if(bug.module) tags.push(`<span class="tag" style="background:#f0f4f8;color:#37474f">${escapeHTML(bug.module)}</span>`);
  if(bug.category) tags.push(`<span class="tag tag-cat-${escapeHTML(bug.category)}">${escapeHTML(bug.category)}</span>`);
  if(!bug.diagnosed) tags.push('<span class="tag tag-warn">⚠ 待诊断</span>');

  const cause = bug.cause ? `
    <div class="section">
      <h3>根因 ${bug.diagnosed_at ? `<span style="font-weight:400;color:#90a4ae;text-transform:none">(${escapeHTML(bug.diagnosed_at)})</span>` : ''}</h3>
      <div class="cause-box">${escapeHTML(bug.cause)}</div>
    </div>` : `<div class="warn-box">⚠ 还没诊断。在 diagnoses.json 加 "${escapeHTML(bug.key)}" 条目即可填入。</div>`;
  const tables = (bug.config_tables && bug.config_tables.length) ? `
    <div class="section">
      <h3>涉及配置表</h3>
      <div class="tables-box">${bug.config_tables.map(t=>`<span class="table-tag">${escapeHTML(t)}</span>`).join('')}</div>
    </div>` : '';
  const suggest = bug.suggestion ? `
    <div class="section">
      <h3>处理建议</h3>
      <div class="suggest-box">${escapeHTML(bug.suggestion)}</div>
    </div>` : '';
  const desc = bug.description.trim() ? `
    <div class="section">
      <h3>Jira 描述</h3>
      <div class="desc-box">${escapeHTML(bug.description)}</div>
    </div>` : '';

  main.innerHTML = `
    <div class="detail-header">
      <div class="detail-key"><a href="${escapeHTML(bug.url)}" target="_blank">${escapeHTML(bug.key)}</a> ↗</div>
      <div class="detail-summary">${escapeHTML(bug.summary)}</div>
      <div class="detail-meta">${tags.join('')}</div>
      <div style="margin-top:6px;font-size:11px;color:#90a4ae">创建 ${escapeHTML(bug.created)} · 更新 ${escapeHTML(bug.updated)}</div>
    </div>
    ${cause}
    ${tables}
    ${suggest}
    ${desc}
  `;
}

document.getElementById('search').oninput = e => { filterText = e.target.value; renderSidebar(); };
renderSidebar();
</script>
</body>
</html>
"""

def main():
    print("Loading diagnoses...")
    diagnoses = json.loads(DIAGNOSES_FILE.read_text(encoding="utf-8"))
    diagnoses = {k: v for k, v in diagnoses.items() if not k.startswith("_")}

    print("Fetching Jira...")
    jira_data = fetch_jira()
    print(f"Got {len(jira_data.get('issues',[]))} issues")

    auth = json.loads(JIRA_AUTH.read_text())
    bugs = merge(jira_data, diagnoses, auth["baseUrl"])

    from datetime import datetime
    build_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    out = HTML_TEMPLATE.replace("__BUGS_JSON__", json.dumps(bugs, ensure_ascii=False))
    out = out.replace("__BUILD_TIME__", build_time)
    OUTPUT_HTML.write_text(out, encoding="utf-8")
    diagnosed = sum(1 for b in bugs if b["diagnosed"])
    print(f"✓ Wrote {OUTPUT_HTML} ({len(bugs)} bugs, {diagnosed} diagnosed)")
    print(f"  open file://{OUTPUT_HTML}")

if __name__ == "__main__":
    main()
