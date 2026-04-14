#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import time
import argparse
import common
from typing import Any, Dict, List, Optional

from query_game import dimension_values

# ---------------------------------------------------------------------------
# 数据读取与筛选
# ---------------------------------------------------------------------------

PREFIX = "material_"
CACHE_TIME = 2 * 3600
CACHE_FUNCTIONS: Dict[str, Any] = {}
cache = common.make_cache(CACHE_FUNCTIONS, PREFIX)
# 固定的维度下拉列表
_DEFAULT_DIM_VALUES = {
	"platform": ["IOS","ANDROID"],
	"test_asset": ["0:素材测试","1:正常广告"],
	"vi_opt": ["VO","OTHER EO","PURCHASE EO","INSTALL","OTHERS"],
	"source": ["facebook","google","toutiao","unity","applovin","moloco","tiktok"],
}
_OTHER_DIM_VALUES = {
	"package_cd": "60d19ec0f8e0ee6ed33cca43"
}
	
def read_cache(func_name: str, params: Optional[Dict[str, Any]]=None) -> List[Any]:
	"""
	Params:
		func_name: @cache缓存过的函数名
		params: 过滤参数
	"""
	result = None
	if func_name not in list(CACHE_FUNCTIONS.keys()):
		return result
	params = params or {}
	_func, filename = CACHE_FUNCTIONS[func_name]
	result, path_time = common.read(filename)
	if result is None or (time.time() - path_time) > CACHE_TIME:
		result = _func(params)
	items = list(result.values()) if isinstance(result, dict) else result
	return items
	
def get_params(params: Dict[str, Any]) -> Dict[List[Any]]:
	"""
	批量查询缓存 
	Return: {"func_name":[ 根据params过滤后的JSON列表 ]}
	"""
	out_info = {}
	funcs = params.get("funcs") or []
	if "ALL" in funcs:
		func_list = list(CACHE_FUNCTIONS.keys())
	else:
		func_list = list(set(CACHE_FUNCTIONS.keys()) & set(funcs))
	for func_name in func_list:
		temp_data = read_cache(func_name, params)
		if len(temp_data) > 0:
			out_info[func_name] = temp_data
	return out_info

# ---------------------------------------------------------------------------
# 内建 API 实现
# ---------------------------------------------------------------------------

def dimension_keys(params: Dict[str, Any]) -> Dict[str, Any]:
	"""
	批量查询维度的可选列表
	Return: [{"维度ID": ["真实值:展示值"],"维度ID####游戏编码": ["真实值"]}]
	"""
	p_ids = params.get("ids") or []
	p_games = params.get("games") or []
	if len(p_ids) == 0:
		raise ValueError(""" 需要通过 -i "维度ID1,维度ID2" 限制指定维度 """)
	out_info = {x:_DEFAULT_DIM_VALUES[x] for x in p_ids if x in _DEFAULT_DIM_VALUES.keys()}
	q_ids = list(set(list(_OTHER_DIM_VALUES.keys())) & set(p_ids))
	for key in q_ids:
		q_params = { "games": p_games, "ids": [_OTHER_DIM_VALUES[key]] }
		for k, v in dimension_values(q_params).items():
			_game = k.split("####")[-1]
			out_info[f"{key}####{_game}"] = v
	return out_info

@cache("jsonl")
def dimensions(params: Dict[str, Any]) -> List[Dict[str, Any]]:
	""" 维度: id,name,provider """
	get_info = common.get("material/dimensions")
	out_info = []
	for x in (get_info.get("data") or []):
		_key = (x.get("key") or "")
		_name = (x.get("name") or "")
		if _key == "" or _name == "":
			continue
		base_dict = { "key": _key, "name": _name}
		if _key in _DEFAULT_DIM_VALUES.keys():
			base_dict["provider"] = 1
		elif _key in _OTHER_DIM_VALUES.keys():
			base_dict["provider"] = 2
		out_info.append(base_dict)
	return out_info

@cache("jsonl")
def indicators(params: Dict[str, Any]) -> List[Dict[str, Any]]:
	""" 指标: id,name """
	get_info = common.get("material/indicators")
	out_info = []
	for x in (get_info.get("data") or []):
		_key = (x.get("key") or "")
		_name = (x.get("name") or "")
		if _key == "" or _name == "":
			continue
		base_dict = { "key": _key, "name": _name}
		out_info.append(base_dict)
	return out_info

def query(params: Dict[str, Any]) -> Any:
	"""查询数据"""
	if not (params.get("startAt") and params.get("endAt")):
		raise ValueError(" --startAt YYYY-MM-DD endAt YYYY-MM-DD 参数不能为空")
	if len(params.get("games") or []) == 0:
		raise ValueError(f"-g 游戏编码1,游戏编码2 不能为空")
	body = {
		"gameCds": params["games"],
		"startAt": params["startAt"], "endAt": params["endAt"], 
		"enablePage": False, "calculateSummary": False, 
		"dimensions": params.get("dimensions") or [],
		"dimensionFilters": params.get("dimensionFilters") or [],
		"indicators": params.get("indicators") or [],
		"indicatorFilters": params.get("indicatorFilters") or [],
	}
	out_info = {}
	query_result = common.post("material/query", json_body=body).get("data") or {}
	if len(body["indicators"]) == 0:
		out_info["result"] = query_result.get("result") or []
		out_info["columns"] = query_result.get("columns") or []
	else:
		filter_keys = body["dimensions"] + body["indicators"]
		out_info["result"] = [ {k:v for k,v in x.items() if k in filter_keys} for x in query_result.get("result") or []]
		out_info["columns"] = [ x for x in query_result.get("columns") or [] if x.get("key") in filter_keys]
	return out_info

# ---------------------------------------------------------------------------
# 命令注册与入口
# ---------------------------------------------------------------------------

BUILTIN_COMMANDS: Dict[str, Any] = {
	"query": query, 
	"get_params": get_params,
	"dimension_keys": dimension_keys,
}


def main() -> None:
	parser = argparse.ArgumentParser(description="查询 Datain 发行素材")
	parser.add_argument("-c", "--command", required=True, default="", help="执行方法")
	parser.add_argument("-f", "--funcs", default="ALL", help="函数名列表")
	parser.add_argument("-g", "--games", default="", help="游戏编码列表")
	parser.add_argument("-i", "--ids", default="", help="ID列表")
	parser.add_argument("--startAt", help="开始日期 YYYY-MM-DD")
	parser.add_argument("--endAt", help="结束日期 YYYY-MM-DD")
	parser.add_argument("--dimensions", default="[]", help="维度 JSON数组")
	parser.add_argument("--dimensionFilters", default="[]", help="维度 过滤JSON数组")
	parser.add_argument("--indicators", default="[]", help="指标 JSON数组")
	parser.add_argument("--indicatorFilters", default="[]", help="指标 过滤JSON数组")
	args = parser.parse_args()

	COMMANDS = BUILTIN_COMMANDS.keys()
	if args.command not in COMMANDS:
		raise ValueError( "用法: python3 query_material.py --command <command>" "command 可取: "+ ", ".join(COMMANDS) )
	params = {
		"startAt": args.startAt, "endAt": args.endAt,
		"dimensions": common.parse_json_arg(args.dimensions),
		"dimensionFilters": common.parse_json_arg(args.dimensionFilters),
		"indicators": common.parse_json_arg(args.indicators),
		"indicatorFilters": common.parse_json_arg(args.indicatorFilters),
		"games": common.parse_json_arg(args.games, "list"), 
		"funcs": common.parse_json_arg(args.funcs, "list"),
		"ids": common.parse_json_arg(args.ids, "list"),
	}
	result = BUILTIN_COMMANDS[args.command](params)
	print(result)


if __name__ == "__main__":
	main()
