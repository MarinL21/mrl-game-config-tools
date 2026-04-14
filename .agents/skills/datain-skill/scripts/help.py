#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import argparse
import common


def filter_search(questions, types):
	result = []
	if types == "showdoc":
		search_result = common.search( 
			query=questions, project_name="datain_docs", table_name="showdoc", 
			top_n=5, search_mode="hybrid", hybrid_weight=0.99, enable_rerank=True, rerank_amplify_factor=8
		)
		items = search_result.get("data",{}).get("results") or []
		for item in items:
			link = (item.get("link") or "").strip()
			text = (item.get("text") or "").strip()
			if link!='' and text!='':
				result.append({"link":link,"text":text})
	else:
		raise ValueError("types 未定义")
	return json.dumps(result, **common._JSON_DUMPS_KW)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Datain小助手：根据问题检索相关文档")
	parser.add_argument("questions", help="检索问题/关键词")
	parser.add_argument("--types", default="showdoc", help="检索类型")
	args = parser.parse_args()

	if not args.questions:
		raise ValueError("请传入检索问题，例如: help.py '如何使用派生指标'")
	print(filter_search(args.questions, args.types))
