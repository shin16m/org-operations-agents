"""In-memory Asana HTTP fake for org-os tests."""
from __future__ import annotations

from copy import deepcopy
from typing import Any


class FakeResponse:
    def __init__(self, payload: dict, *, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> dict:
        return self._payload


class FakeAsanaBackend:
    """Minimal Asana API stub backed by in-memory task dicts."""

    def __init__(self, tasks: dict[str, dict], *, project_gid: str = "PROJ") -> None:
        self.tasks = {gid: deepcopy(task) for gid, task in tasks.items()}
        self.project_gid = project_gid
        self.put_calls: list[dict] = []

    def get(self, url: str, **kwargs: Any) -> FakeResponse:
        if f"/projects/{self.project_gid}/tasks" in url:
            return FakeResponse({"data": list(self.tasks.values())})
        if "/tasks/" in url:
            gid = url.split("/tasks/")[1].split("?")[0]
            task = self.tasks.get(gid)
            if task is None:
                return FakeResponse({"data": {}}, status_code=404)
            return FakeResponse({"data": deepcopy(task)})
        return FakeResponse({"data": {}}, status_code=404)

    def put(self, url: str, **kwargs: Any) -> FakeResponse:
        gid = url.split("/tasks/")[1].split("?")[0]
        body = kwargs.get("json") or {}
        data = body.get("data") or {}
        custom_fields = data.get("custom_fields") or {}
        self.put_calls.append({"gid": gid, "custom_fields": custom_fields})
        task = self.tasks.setdefault(gid, {"gid": gid, "custom_fields": []})
        cf_list = list(task.get("custom_fields") or [])
        for field_gid, enum_gid in custom_fields.items():
            updated = False
            for cf in cf_list:
                if str(cf.get("gid")) == str(field_gid):
                    if enum_gid is None:
                        cf["enum_value"] = None
                    else:
                        cf["enum_value"] = {"gid": enum_gid, "name": enum_gid}
                    updated = True
                    break
            if not updated:
                cf_list.append(
                    {
                        "gid": field_gid,
                        "enum_value": None if enum_gid is None else {"gid": enum_gid, "name": enum_gid},
                    }
                )
        task["custom_fields"] = cf_list
        self.tasks[gid] = task
        return FakeResponse({"data": deepcopy(task)})
