import asyncio
import functools
import inspect
from typing import Any, Callable, Coroutine, Optional, TypeVar, Union

from langchain_core.runnables import RunnableLambda

Output = TypeVar("Output")
SyncFunc = Callable[..., Output]
AsyncFunc = Callable[..., Coroutine[Any, Any, Output]]
AnyFunc = Union[SyncFunc[Output], AsyncFunc[Output]]


def _adapt(func: SyncFunc[Output]) -> SyncFunc[Output]:
    """Adapt multi-param sync function to single-param."""
    n = len(inspect.signature(func).parameters)
    if n == 1:
        return func

    @functools.wraps(func)
    def w(x: Any) -> Output:
        if n == 0:
            return func()
        if isinstance(x, dict):
            return func(**x)
        if isinstance(x, (list, tuple)):
            return func(*x)
        return func(x)
    return w


def _adapt_async(func: AsyncFunc[Output]) -> AsyncFunc[Output]:
    """Adapt multi-param async function to single-param."""
    n = len(inspect.signature(func).parameters)
    if n == 1:
        return func

    @functools.wraps(func)
    async def w(x: Any) -> Output:
        if n == 0:
            return await func()
        if isinstance(x, dict):
            return await func(**x)
        if isinstance(x, (list, tuple)):
            return await func(*x)
        return await func(x)
    return w


def _sync_fallback(afunc: AsyncFunc[Output]) -> SyncFunc[Output]:
    """Create sync fallback for async function."""
    @functools.wraps(afunc)
    def w(x: Any) -> Output:
        try:
            asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as e:
                return e.submit(asyncio.run, afunc(x)).result()
        except RuntimeError:
            return asyncio.run(afunc(x))
    return w


def to_runnable(
    func: AnyFunc[Output],
    *,
    name: Optional[str] = None,
) -> RunnableLambda:
    """
    Convert any function (sync or async) to a RunnableLambda.

    Automatically detects sync/async and wraps appropriately,
    enabling callback support in LangChain/LangGraph pipelines.

    Args:
        func: The function to convert (sync or async).
        name: Optional name for the runnable.

    Returns:
        A RunnableLambda wrapping the function.

    """
    n = name or func.__name__

    if asyncio.iscoroutinefunction(func):
        af = _adapt_async(func)
        return RunnableLambda(func=_sync_fallback(af), afunc=af, name=n)
    return RunnableLambda(func=_adapt(func), name=n)
