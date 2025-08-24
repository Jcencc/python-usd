# -*- coding: utf-8 -*-
# Jcen
import json
import time

from behavior_tree.core import (
    BehaviorTree, Action, Condition, Status, Blackboard, MockBackendFetcher
)



if __name__ == "__main__":

    # 你的JSON数据
    with open(r'./sample.json', 'r', encoding='utf-8') as f:
        behavior_json = json.load(f)

    blackboard = Blackboard()
    root_node = BehaviorTree.json_to_node(behavior_json, blackboard=blackboard)

    bt = BehaviorTree(root=root_node, blackboard=blackboard)
    blackboard = bt.blackboard
    # （可选）设置黑板数据（影响条件判断）
    # 1. 配置项目与流程的对应关系

    # 设置usd创建usd的一些数据
    if behavior_json.get('type') == 'Blackboard':
        for key, value in behavior_json.get('custom_properties', {}).items():
            blackboard.set(key, value)
    if behavior_json.get('json_file'):
        with open(behavior_json.get('json_file'), 'r', encoding='utf-8') as f:
            blackboard_data = json.load(f)
        for key, value in blackboard_data.items():
            blackboard.set(key, value)

    status = bt.tick()


    print(f"行为树执行状态: {status}")
