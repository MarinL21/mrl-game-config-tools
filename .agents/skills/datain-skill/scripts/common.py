#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import requests
from typing import Any, Callable, Dict, List, Optional

# 紧凑 JSON，无多余空白，体积最小且可读
_JSON_DUMPS_KW = {"ensure_ascii": False, "separators": (",", ":")}

# ---------------------------------------------------------------------------
# 读取配置
# ---------------------------------------------------------------------------

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.normpath(os.path.join(_SCRIPTS_DIR, ".."))

_configs_cache: Dict[str, Any] = {}
def get_config(key: str, reload: bool = False) -> Dict[str, List[str]]:
	"""读取 assets/configs.json 并缓存，reload=True 强制重新读取。"""
	global _configs_cache
	if _configs_cache and not reload:
		return _configs_cache.get(key)
	with open(os.path.join(_PROJECT_ROOT, "./assets/configs.json"), "r", encoding="utf-8") as f:
		_configs_cache = json.load(f)
	return _configs_cache.get(key)

# ---------------------------------------------------------------------------
# 常用函数
# ---------------------------------------------------------------------------

def has_intersection(list1: Any, list2: Any) -> bool:
	"""两个列表是否有交集。"""
	if isinstance(list1, list) and isinstance(list2, list):
		list1 = [str(x).strip() for x in list1 if str(x).strip()!=""]
		list2 = [str(x).strip() for x in list2 if str(x).strip()!=""]
		if len(list1) == 0:
			return True  
		if len(list2) == 0:
			return True
		return len(list(set(list1) & set(list2)))>0
	else:
		return True

def parse_json_arg(value: str, types="json") -> Any:
	"""参数解析"""
	if types == "json":
		return json.loads(value)
	elif types == "list":
		return [x.strip() for x in value.split(",") if x.strip()!=""]
	else:
		return value

def is_date_format(date_str):
	"""字符串是否是日期"""
	import re
	pattern = r'^\d{4}-\d{2}-\d{2}$'
	if len(date_str)!=10:
		return False
	if re.fullmatch(pattern, date_str):
		return True
	return False

# ---------------------------------------------------------------------------
# 文件缓存和读取
# ---------------------------------------------------------------------------

# 缓存路径, 默认当前 skills 下的 assets 文件夹
# 相对路径基于项目根目录解析
_cache_dir_raw = get_config("cache_dir")
_CACHE_DIR = (
	os.path.join(_PROJECT_ROOT, _cache_dir_raw) 
	if _cache_dir_raw and not os.path.isabs(_cache_dir_raw) 
	else _cache_dir_raw
)

def read(filename: str) -> Any:
	"""读取 _CACHE_DIR 目录下的 filename 文件内容，根据扩展名自动选择解析方式。
	"""
	path = os.path.join(_CACHE_DIR, filename)
	if not os.path.isfile(path):
		return None, None
	ext = os.path.splitext(path)[1].lower()[1:]
	path_time = os.path.getmtime(path)
	with open(path, "r", encoding="utf-8") as f:
		if ext == "json":
			result = json.load(f)
		elif ext == "jsonl":
			out: List[Dict[str, Any]] = []
			for line in f:
				line = line.strip()
				if not line:
					continue
				out.append(json.loads(line))
			result = out
		else:
			result = f.read()
	return result, path_time

def write(filename: str, data: Any) -> None:
	"""将数据写入 _CACHE_DIR 目录下的 filename 文件，根据 data 类型自动选择序列化方式。
	"""
	path = os.path.join(_CACHE_DIR, filename)
	ext = os.path.splitext(path)[1].lower()[1:]
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		if isinstance(data, dict) and ext == "json" and data!={}:
			json.dump(data, f, **_JSON_DUMPS_KW)
		elif isinstance(data, list) and ext == "jsonl" and len(data) > 0:
			for item in data:
				f.write(json.dumps(item, **_JSON_DUMPS_KW) + "\n")
		elif str(data) != "":
			f.write(data if isinstance(data, str) else str(data))

def make_cache(registry: Dict[str, Callable], prefix: str) -> Callable:
	"""创建绑定到指定注册表的 cache 装饰器。
	支持 @cache 和 @cache("json") 两种用法。
	"""
	def _resolve_ext(result: Any, ext: Optional[str] = None) -> str:
		if ext is not None:
			return ext
		if isinstance(result, list):
			return "jsonl"
		if isinstance(result, dict):
			return "json"
		return "txt"

	def _wrap(func: Callable, ext: Optional[str] = None) -> Callable:
		def wrapper(params: Dict[str, Any]) -> Any:
			result = func(params)
			resolved = _resolve_ext(result, ext)
			filename = f"{prefix}{func.__name__}.{resolved}"
			write(filename, result)
			registry[func.__name__] = (wrapper, filename)
			return result
		registry[func.__name__] = (wrapper, f"{prefix}{func.__name__}.{ext or 'jsonl'}")
		return wrapper

	def cache(ext=None):
		if isinstance(ext, str):
			return lambda func: _wrap(func, ext)
		return _wrap(ext)

	return cache


def keyed_cache(filename: str, cache_time: int):
	"""按参数组合 key 的文件缓存装饰器，同一文件内各 key 独立过期。
	cache key 由函数的非 None 参数以 '####' 拼接生成。
	"""
	def decorator(func):
		def wrapper(*args):
			_uniq_id = "####".join(str(a) for a in args if a is not None)
			now_time = time.time()
			cache_info, _ = read(filename)
			cache_info = cache_info if cache_info else {}
			if _uniq_id in cache_info:
				entry = cache_info[_uniq_id]
				if now_time - entry.get("time", 0) <= cache_time:
					return entry.get("values") or []
			result = func(*args)
			cache_info[_uniq_id] = {"time": now_time, "values": result}
			cache_info = {k: v for k, v in cache_info.items() if now_time - v.get("time", 0) <= cache_time}
			write(filename, cache_info)
			return result
		return wrapper
	return decorator


# ---------------------------------------------------------------------------
# 请求 datain API
# ---------------------------------------------------------------------------

TIMEOUT = 30
BASE_URL = get_config("datain_api_url")

def get_api_key() -> str:
	"""从环境变量读取 DATAIN_API_KEY """
	key = os.getenv("DATAIN_API_KEY", "").strip()
	if key:
		return key
	raise Exception(
		"请在当前系统的环境变量中设置 DATAIN_API_KEY\n"
		"获取途径: https://datain.tap4fun.com/ -> 个人中心 -> 设置 -> APP KEY"
	)

def get(
	path: str, 
	params: Optional[Dict[str, Any]] = None, 
	api_key: Optional[str] = None
) -> Dict[str, Any]:
	"""GET 请求。path 为相对路径（如 common/indicator/list）。自动附带 api_key。"""
	key = api_key or get_api_key()
	url = f"{BASE_URL}/{path.lstrip('/')}"
	p = dict(params) if params else {}
	p["api_key"] = key
	resp = requests.get(url, params=p, timeout=TIMEOUT)
	resp.raise_for_status()
	return resp.json()

def post(
	path: str,
	json_body: Optional[Dict[str, Any]] = None,
	api_key: Optional[str] = None,
) -> Dict[str, Any]:
	"""POST 请求。path 为相对路径。自动附带 api_key 为查询参数。"""
	key = api_key or get_api_key()
	url = f"{BASE_URL}/{path.lstrip('/')}"
	resp = requests.post(url, params={"api_key": key}, json=json_body or {}, timeout=TIMEOUT)
	resp.raise_for_status()
	return resp.json()

# ---------------------------------------------------------------------------
# rag检索服务
# ---------------------------------------------------------------------------

RAG_URL = get_config("rag_url")

def search(
	query: str, project_name: str, table_name: str,
	top_n: int = 5,
	search_mode: str = "hybrid",
	hybrid_weight: float = 0.7,
	tokenize_query: bool = False,
	enable_rerank: bool = False,
	rerank_amplify_factor: float = 1.0,
	where: Optional[str] = None,
) -> dict:
	"""调用向量检索 API 进行搜索。
	Args:
		query: 检索内容。
		project_name: 项目名。
		table_name: 表名。
		top_n: 返回条数，范围 1~1000，默认 10。
		search_mode: 检索模式，可选 keyword / vector / hybrid，默认 hybrid。
		hybrid_weight: 向量权重，0.0~1.0，默认 0.7。
		tokenize_query: 是否对 query 进行 jieba 分词 + 停用词过滤，默认 False。
		enable_rerank: 是否启用 BGE Reranker 重排，默认 False。
		rerank_amplify_factor: 重排放大系数，必须 >= 1.0，默认 1.0。
		where: WHERE 条件 SQL 片段，如 "department='人事部' AND level='P7'"。
	Returns:
		API 返回的 JSON 响应。
	"""
	# --- 参数校验 ---
	if not isinstance(query, str) or not query.strip():
		raise ValueError("query 必须是非空字符串")
	if not isinstance(project_name, str) or not project_name.strip():
		raise ValueError("project_name 必须是非空字符串")
	if not isinstance(table_name, str) or not table_name.strip():
		raise ValueError("table_name 必须是非空字符串")
	if not isinstance(top_n, int) or not 1 <= top_n <= 5:
		raise ValueError(f"top_n 必须是 1~5 的整数，当前值: {top_n}")
	valid_modes = {"keyword", "vector", "hybrid"}
	if search_mode not in valid_modes:
		raise ValueError(f"search_mode 必须是 {valid_modes} 之一，当前值: {search_mode!r}")
	if not isinstance(hybrid_weight, (int, float)) or not 0.0 <= hybrid_weight <= 1.0:
		raise ValueError(f"hybrid_weight 必须在 0.0~1.0 之间，当前值: {hybrid_weight}")
	if not isinstance(rerank_amplify_factor, (int, float)) or rerank_amplify_factor < 1.0 or top_n*rerank_amplify_factor > 100:
		raise ValueError(f"rerank_amplify_factor 必须 >= 1.0 且 top_n*rerank_amplify_factor <= 100，当前值: {rerank_amplify_factor}")
	if where is not None and (not isinstance(where, str) or not where.strip()):
		raise ValueError("where 如果提供则必须是非空字符串")
	
	# --- 构建请求 ---
	payload = {
		"query": query.strip(),
		"project_name": project_name.strip(),
		"table_name": table_name.strip(),
		"top_n": top_n,
		"search_mode": search_mode,
		"hybrid_weight": float(hybrid_weight),
		"tokenize_query": tokenize_query,
		"enable_rerank": enable_rerank,
		"rerank_amplify_factor": float(rerank_amplify_factor),
	}
	if where is not None:
		payload["where"] = where.strip()
	resp = requests.post(RAG_URL, json=payload, timeout=30)
	resp.raise_for_status()
	return resp.json()

