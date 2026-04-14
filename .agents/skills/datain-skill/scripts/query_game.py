#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import time
import argparse
import common
import json
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# 数据读取与筛选
# ---------------------------------------------------------------------------

# 定义缓存装饰器
PREFIX = "game_"
CACHE_TIME = 2 * 3600
CACHE_FUNCTIONS: Dict[str, Any] = {}
cache = common.make_cache(CACHE_FUNCTIONS, PREFIX)


def get_leaf_paths(obj, prefix_name) -> List[Any]:	
	"""
	解析json_value
	"""
	result = []
	for key, value in obj.items():
		current = f"{prefix_name}.{key}" if prefix_name else key
		if isinstance(value, dict) and "type" in value:
			value["name"] = current
			result.append(value)
		elif isinstance(value, dict):
			result.extend(get_leaf_paths(value, current))
	return result


def _filter_items(items: List[Dict], params: Dict[str, Any], data_format: str) -> List[Any]:
	"""
	根据 params（algorithmId、games、ids、names）筛选 items 列表
	Return:
		data_format=src: 原始格式的列表
		data_format=name: 只包含name的列表
	"""
	out_info: List[Any] = []
	params = params or {}
	p_ids = params.get("ids") or []
	p_names = params.get("names") or []
	p_games = params.get("games") or []
	p_algorithmId = [params.get("algorithmId") or ""]
	for item in items:
		_id = item.get("id") or ""
		_ids = item.get("ids") or []
		_name = item.get("name") or ""
		_type = item.get("type") or ""
		_games = item.get("games") or []
		_json_value = get_leaf_paths(item.get("json_value") or {}, _name)
		_algorithm_id = item.get("algorithmId") or []
		if not common.has_intersection(p_ids, [(x.get("id") or "") for x in _ids] + [_id]):
			continue
		if not common.has_intersection(p_names, [_name,_type]):
			continue
		if not common.has_intersection(p_games, _games):
			continue
		if not common.has_intersection(p_algorithmId, _algorithm_id):
			continue
		if data_format == "name":
			if len(_json_value) > 0:
				out_info.extend([x.get("name","") for x in _json_value if x.get("name","")!=""])
			elif _name != "":
				out_info.append(_name)
			elif _type != "":
				out_info.append(_type)
		else:
			if len(_json_value) > 0:
				out_info.append({"id": _id, "json_value": _json_value})
			else:
				out_info.append(item)
	return out_info

def read_cache(func_name: str, params: Optional[Dict[str, Any]], data_format: str="src") -> List[Any]:
	"""
	Params:
		func_name: @cache缓存过的函数名
		params: 过滤参数
		data_format: 返回格式( src, name )
	"""
	result = []
	if func_name not in list(CACHE_FUNCTIONS.keys()):
		return result
	params = params or {}
	_func, filename = CACHE_FUNCTIONS[func_name]
	result, path_time = common.read(filename)
	if result is None or (time.time() - path_time) > CACHE_TIME:
		result = _func(params)
	items = list(result.values()) if isinstance(result, dict) else result
	filter_items = _filter_items(items, params, data_format)
	return filter_items

def get_cache_funcs(params: Dict[str, Any], data_format: str) -> Dict[List[Any]]:
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
		temp_data = read_cache(func_name, params, data_format)
		if len(temp_data) > 0:
			out_info[func_name] = temp_data
	return out_info

# ---------------------------------------------------------------------------
# 内建 API 实现
# ---------------------------------------------------------------------------

GAME_DEMENSION_NAME = "游戏"
GAME_DEMENSION_ID = "60d0270962a4005e8b481e1f"

@common.keyed_cache(f"{PREFIX}dimension_values.json", CACHE_TIME)
def dimension_value_list(_id, _game:str=None) -> List[str, Any]:
	"""
	指定 维度ID + 游戏编码 的可选列表, 每个 _uniq_id 单独缓存
	Return: [{"value": value,"name": name}]
	"""
	body = {}
	if _game:
		body["wheres"] = [{"id": GAME_DEMENSION_ID, "name": GAME_DEMENSION_NAME, "operator": "CONTAINS", "value": [_game]}]
	value_list = []
	get_info = common.post(f"common/dimension/{_id}", json_body=body)
	for x in get_info.get("data") or []:
		name, value = x.get("name"), x.get("value")
		if common.is_date_format(value):
			continue
		elif name == value:
			base_dict = {"value": value}
		else:
			base_dict = {"value": value,"name": name}
		value_list.append(base_dict)
	return value_list

def games(params: Dict[str, Any]) -> Dict[str, Any]:
	"""
	游戏编码的可选列表 + 自定义游戏别名games
	Return: {"游戏编码": ["游戏别名"]}
	"""
	out_info = {}
	other_names = common.get_config("games") or {}
	for x in dimension_value_list(GAME_DEMENSION_ID) or []:
		value = x.get("value") or ""
		name = x.get("name") or ""
		if name=="" or value=="":
			continue
		out_info[value] = [name]
		name_list = other_names.get(value) or []
		if len(name_list) > 0:
			out_info[value].extend(name_list)	
	return out_info

def dimension_values(params: Dict[str, Any]) -> Dict[str, Any]:
	"""
	批量查询维度的可选列表
	Return: [{"维度ID": ["真实值:展示值"],"维度ID####游戏编码": ["真实值"]}]
	"""
	out_info = {}
	p_games = set(params.get("games") or [])
	if len((params.get("ids") or [])) == 0 and len(params.get("names") or []) == 0:
		raise ValueError(""" 查询维度的可选列表, -i "维度ID1,维度ID2" 或 -n "维度名1,维度名2" 至少需要需要一个 """)
	for x in read_cache("dimensions", params)  or []:
		_id = x.get("id") or ""
		_name = x.get("name") or ""
		_games = x.get("games") or []
		_provider = x.get("provider")
		if _provider==1:
			_tmp = dimension_value_list(_id)
			if len(_tmp) > 0:
				out_info[_id] = [":".join([x.get("value"), x.get("name") or ""]) for x in _tmp]
		elif _provider==2:
			if len(p_games) == 0:
				raise ValueError(f""" 维度 {_name}({_id}) 需要限制 -g "游戏编码1,游戏编码2"  """)
			f_games = list(set(_games)&p_games) if len(_games)>0 else list(p_games)
			if len(f_games) == 0:
				raise ValueError(f""" 维度 {_name}({_id}) 仅可取游戏 {_games}  """)
			for _game in f_games:
				_tmp = dimension_value_list(_id,_game)
				if len(_tmp) > 0:
					out_info[f"{_id}####{_game}"] = [":".join([x.get("value"), x.get("name") or ""]) for x in _tmp]
	return out_info

@cache("jsonl")
def dimensions(params: Dict[str, Any]) -> List[Dict[str, Any]]:
	""" 维度: id,name,games,algorithmId,disableGroupBy,provider """
	get_info = common.get("basic/dimensions", params={"pageId":"GAME_DATA"})
	out_info = []
	for x in (get_info.get("data") or []):
		_id = (x.get("id") or "")
		_name = (x.get("name") or "")
		if _id == "" or _name == "":
			continue
		base_dict = { "id": _id, "name": _name}
		_games = (x.get("games") or [])
		if len(_games) > 0:
			base_dict.update({"games": _games})
		_algorithmId = (x.get("algorithmId") or [])
		if len(_algorithmId) == 1:
			base_dict.update({"algorithmId": _algorithmId})
		_disableGroupBy = (x.get("disableGroupBy") or False)
		if _disableGroupBy:
			base_dict.update({"disableGroupBy": _disableGroupBy})
		_providerType = (x.get("providerType") or "")
		if _providerType!="":
			_provider = (x.get("providerRelatedVariables") or [])
			base_dict.update({"provider": len(_provider)+1})
		_jsonValue= (x.get("jsonValue") or "")
		if _jsonValue!="":
			base_dict.update({"json_value": json.loads(_jsonValue)})
		out_info.append(base_dict)
	return out_info

@cache("jsonl")
def tags(params: Dict[str, Any]) -> List[Dict[str, Any]]:
	""" 标签: id,name """
	get_info = common.get("common/user-tag/list")
	out_info = []
	for x in get_info.get("data") or []:
		_id = (x.get("id") or "")
		_name = (x.get("name") or "")
		_game = str(x.get("game") or 0)
		if _id == "" or _name == "" or _game=="0":
			continue
		out_info.append({"id": _id, "name": _name, "games": [_game]})
	return out_info

@cache("jsonl")
def indicators(params: Dict[str, Any]) -> List[Dict[str, Any]]:
	""" 常规指标: id,name,games,cohort,cohortUtils """
	get_info = common.get("common/indicator/list")
	out_info = []
	for x in get_info.get("data") or []:
		_id = (x.get("id") or "")
		_name = (x.get("name") or "")
		if _id == "" or _name == "":
			continue
		base_dict = {"id": _id, "name": _name}
		_games = (x.get("games") or [])
		if len(_games) > 0:
			base_dict.update({"games": _games})
		_cohort = (x.get("cohort") or False)
		_cohortUtils = (x.get("cohortUtils") or [])
		if _cohort and len(_cohortUtils)>0:
			base_dict.update({"cohort": _cohort, "cohortUtils": _cohortUtils})
		out_info.append(base_dict)
	return out_info

@cache("jsonl")
def derived_indicators(params: Dict[str, Any]) -> List[Dict[str, Any]]:
	""" 派生指标: id,name,rely_ids """
	get_info = common.get("common/derived-column/list")
	out_info = []
	for x in get_info.get("data") or []:
		_id = (x.get("id") or "")
		_name = (x.get("name") or "")
		_columnsInfo = (x.get("columnsInfo") or [])
		_rely_ids = [_ids.get("id") for _ids in _columnsInfo if _ids.get("id")]
		if _id == "" or _name == "" or len(_rely_ids)==0:
			continue
		out_info.append({"id": _id, "name": _name, "rely_ids": _rely_ids})
	return out_info	
	
@cache("json")
def map_indicators(params: Dict[str, Any]) -> Dict[str, Any]:
	""" map指标: type,ids[id,name],games,cohort,cohortUtils """
	get_info = common.get("basic/map/indicators", params={"pageId":"GAME_DATA"})
	out_dict = {}
	for x in get_info.get("data") or []:
		_id = (x.get("id") or "")
		_name = (x.get("name") or "")
		_type = (x.get("mapIndicatorType") or "") 
		_value = (x.get("mapIndicatorValue") or "") 
		if _id == "" or _name == "" or _type=="":
			continue
		_games = (x.get("games") or [])
		_cohort = (x.get("cohort") or False)
		_cohortUtils = (x.get("cohortUtils") or [])
		_uniq_id = "_".join([_type, "1" if _cohort else "0"]+_games)
		if _uniq_id not in out_dict.keys():
			base_dict = {"type":_type,"ids":[{"id": _id, "name":_value}]}
			if len(_games) > 0:
				base_dict.update({"games": _games})
			if _cohort and len(_cohortUtils)>0:
				base_dict.update({"cohort": _cohort, "cohortUtils": _cohortUtils})
			out_dict[_uniq_id] = base_dict
		else:
			out_dict[_uniq_id]["ids"].append({"id": _id, "name":_value})
	return out_dict

def query(params: Dict[str, Any]) -> Any:
	"""查询数据"""
	body = dict(params)
	if not (params.get("startAt") and params.get("endAt")):
		raise ValueError(" --startAt YYYY-MM-DD endAt YYYY-MM-DD 参数不能为空")
	if len(params.get("indicators") or []) == 0:
		raise ValueError(""" --indicators '[{{"id":"指标ID","name":"指标名"}}]' 不能为空 """)
	game_filters = [x for x in params.get("dimensionFilters") or [] if x.get("id")==GAME_DEMENSION_ID]
	if len(game_filters) == 0:
		p_games = params.get("games") or []
		if len(p_games) > 0:
			params["dimensionFilters"].append({"id": GAME_DEMENSION_ID, "name": GAME_DEMENSION_NAME, "operator": "CONTAINS", "value": p_games})
		else:
			raise ValueError(f"""请通过 -g 游戏编码1,游戏编码2 或 --dimensionFilters '[{{"id":"{GAME_DEMENSION_ID}","name":"{GAME_DEMENSION_NAME}","operator":"CONTAINS","value":["游戏编码1","游戏编码2"]}}]' 限制查询指定游戏的数据 """)
	body = {
		"enablePage": False,
		"startAt": params["startAt"], "endAt": params["endAt"],  
		"algorithmId": params.get("algorithmId") or "open_udid",
		"fullDayLimit": int(params.get("fullDayLimit") or 1),
		"dimensions": params.get("dimensions") or [],
		"dimensionFilters": params.get("dimensionFilters") or [],
		"indicators": params.get("indicators") or [],
		"indicatorFilters": params.get("indicatorFilters") or [],
		"tagDimensions": params.get("tagDimensions") or [],
		"tagFilters": params.get("tagFilters") or [],
		"jsonDimensions": params.get("jsonDimensions") or [],
	}
	out_info = {}
	query_result = common.post("api/game/data/query", json_body=body).get("data") or {}
	if query_result != {}:
		out_info["result"] = [ {k:v for k,v in x.items() if k !="is_current"} for x in query_result.get("result") or []]
		out_info["columns"] = query_result.get("columns") or []
	return out_info
	
# ---------------------------------------------------------------------------
# 命令注册与入口
# ---------------------------------------------------------------------------

BUILTIN_COMMANDS: Dict[str, Any] = {
	"games": games, "query": query,
	"dimension_values": dimension_values,
	"get_param_names": lambda params: get_cache_funcs(params, "name"),
	"get_param_details": lambda params: get_cache_funcs(params, "src"),
}


def main() -> None:
	parser = argparse.ArgumentParser(description="查询 Datain 游戏数据")
	parser.add_argument("-c", "--command", required=True, default="", help="执行方法")
	parser.add_argument("-f", "--funcs", default="ALL", help="函数名列表")
	parser.add_argument("-g", "--games", default="", help="游戏编码列表")
	parser.add_argument("-n", "--names", default="", help="名字列表")
	parser.add_argument("-i", "--ids", default="", help="ID列表")
	parser.add_argument("--startAt", help="开始日期 YYYY-MM-DD")
	parser.add_argument("--endAt", help="结束日期 YYYY-MM-DD")
	parser.add_argument("--algorithmId", default="open_udid", help="归因算法，默认 open_udid")
	parser.add_argument("--fullDayLimit", default="1", help="Cohort足天限制")
	parser.add_argument("--dimensions", default="[]", help="维度 JSON数组")
	parser.add_argument("--jsonDimensions", default="[]", help="JSON维度 JSON数组")
	parser.add_argument("--dimensionFilters", default="[]", help="维度 过滤JSON数组")
	parser.add_argument("--indicators", default="[]", help="指标 JSON数组")
	parser.add_argument("--indicatorFilters", default="[]", help="指标 过滤JSON数组")
	parser.add_argument("--tagDimensions", default="[]", help="标签 JSON数组")
	parser.add_argument("--tagFilters", default="[]", help="标签 过滤JSON数组")
	args = parser.parse_args()

	COMMANDS = BUILTIN_COMMANDS.keys()
	if args.command not in COMMANDS:
		raise ValueError( "用法: python3 query_game.py --command <command>" "command 可取: "+ ", ".join(COMMANDS) )
	if args.algorithmId not in [ "open_udid", "user_id" ]:
		raise ValueError("--algorithmId 只可以取 open_udid 或 user_id")
	if args.fullDayLimit not in [ "0", "1" ]:
		raise ValueError("--fullDayLimit 只可以取 0 或 1")
	params = {
		"algorithmId": args.algorithmId,
		"fullDayLimit": int(args.fullDayLimit),
		"startAt": args.startAt, "endAt": args.endAt,
		"dimensions": common.parse_json_arg(args.dimensions),
		"jsonDimensions": common.parse_json_arg(args.jsonDimensions),
		"dimensionFilters": common.parse_json_arg(args.dimensionFilters),
		"indicators": common.parse_json_arg(args.indicators),
		"indicatorFilters": common.parse_json_arg(args.indicatorFilters),
		"tagDimensions": common.parse_json_arg(args.tagDimensions),
		"tagFilters": common.parse_json_arg(args.tagFilters),
		"funcs": common.parse_json_arg(args.funcs, "list"),
		"games": common.parse_json_arg(args.games, "list"), 
		"names": common.parse_json_arg(args.names, "list"),
		"ids": common.parse_json_arg(args.ids, "list"),
	}
	result = BUILTIN_COMMANDS[args.command](params)
	print(result)


if __name__ == "__main__":
	main()
