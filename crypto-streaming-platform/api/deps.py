from __future__ import annotations

from fastapi import Request

from api.storage_repo import StorageRepo


def get_repo(request: Request) -> StorageRepo:
    return request.app.state.repo
