import os
from langchain_core.runnables import RunnableConfig
from utils.log.node_log import Logger


def init_run_config(graph, ctx):
    tracer = Logger(graph, ctx)
    tracer.on_chain_start = tracer.on_chain_start_graph  # 非必须
    tracer.on_chain_end = tracer.on_chain_end_graph
    config = RunnableConfig(
        callbacks=[
            tracer
        ],
    )
    return config


def init_agent_config(graph, ctx):
    config = RunnableConfig(
        callbacks=[
        ]
    )
    print("config", config)
    return config


# 保留add_trace_tags函数，作为对trace.set_tags的简单包装
def add_trace_tags(trace, tags):
    """
    为trace添加标签
    :param trace: trace对象
    :param tags: 标签字典
    """
    # 使用set_tags方法
    trace.set_tags(tags)

