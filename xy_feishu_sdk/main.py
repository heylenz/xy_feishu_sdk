import json
# disable pylint's E0611: Using the global statement
from feishu import FeishuClient
from requests_toolbelt import MultipartEncoder


class XYFeishuSDK(object):
    def __init__(self, app_id, app_secret) -> None:
        super().__init__()
        self.client = FeishuClient(app_id, app_secret)

    def get_users_open_id(self, emails, user_id_type="open_id"):

        params = {"user_id_type": user_id_type}
        response = self.client.request(
            "POST",
            "/contact/v3/users/batch_get_id",
            params,
            {"user_id_type": "open_id", "emails": emails},
        )
        if response["code"] == 0:
            return {
                user["email"]: user.get("user_id")
                for user in response["data"]["user_list"]
            }

    def get_chats_by_robot(self):
        response = self.client.request("GET", "/im/v1/chats")
        if response["code"] == 0:
            return response["data"]["items"]

    def send_message(
            self, receive_id, content, receive_id_type="open_id", msg_type="text"
    ):

        params = {"receive_id_type": receive_id_type}
        req = {
            "receive_id": receive_id,
            "content": json.dumps(content),
            "msg_type": msg_type,
        }

        payload = json.dumps(req)
        return self.client.request(
            "POST", "/im/v1/messages", data=payload, params=params
        )

    def send_message_to_chat(self, chat_id, content, msg_type="text"):
        params = {"receive_id_type": "chat_id"}
        req = {
            "receive_id": chat_id,
            "content": json.dumps(content),
            "receive_id_type": "chat_id",
            "msg_type": msg_type,
        }

        payload = json.dumps(req)
        return self.client.request(
            "POST", "/im/v1/messages", data=payload, params=params
        )

    def upload_image(self, image_path):
        form = {"image_type": "message", "image": (open(image_path, "rb"))}

        multi_form = MultipartEncoder(form)
        headers = {"Content-Type": multi_form.content_type}
        xx = self.client.request(
            "POST", "/im/v1/images", data=multi_form, headers=headers
        )

        if xx["code"] == 0:
            return xx["data"]["image_key"]

    def upload_image_v1(self, image_io):
        form = {"image_type": "message", "image": image_io}
        multi_form = MultipartEncoder(form)
        headers = {"Content-Type": multi_form.content_type}
        xx = self.client.request(
            "POST", "/im/v1/images", data=multi_form, headers=headers
        )

        if xx["code"] == 0:
            return xx["data"]["image_key"]

    def batch_send_message(self, open_ids, content, msg_type="text"):

        if msg_type != "interactive":
            req = {"msg_type": msg_type, "open_ids": open_ids, "content": content}
        else:
            req = {"msg_type": msg_type, "open_ids": open_ids, "card": content}

        xx = self.client.request(
            "POST", "/message/v4/batch_send/", data=json.dumps(req)
        )
        if xx["code"] == 0:
            return xx["data"]["message_id"]

    def get_chat_users(self, chat_id, emails=None, names=None, open_ids=None):
        results = []

        if emails:
            users_open_id = self.get_users_open_id(emails)
            open_ids = [users_open_id[email] for email in emails]

        params = {"member_id_type": "open_id"}
        response = self.client.request(
            "GET", "/im/v1/chats/{}/members".format(chat_id), params=params
        )
        if response["code"] == 0:
            results.extend(response["data"]["items"])

        while response.get("has_more"):
            params = {
                "member_id_type": "open_id",
                "page_token": response.get("page_token"),
            }
            response = self.client.request(
                "GET", "/im/v1/chats/{}/members".format(chat_id), params=params
            )
            if response["code"] == 0:
                results.extend(response["data"]["items"])

        if names:
            results = [k for k in results if k["name"] in names]

        if open_ids:
            results = [k for k in results if k["member_id"] in open_ids]

        return results

    def format_emails_at(self, emails):
        s = ""
        users = self.get_users_open_id(emails)
        for email, open_id in users.items():
            if open_id:
                s += f"<at email={email}></at>"
            else:
                name = email.split("@")[0]
                s += name
        return s

    def create_task(
            self,
            summary,
            description=None,
            extra=None,
            due=None,
            origin=None,
            can_edit=False,
            collaborators=None,
    ):
        params = {"user_id_type": "open_id"}

        req = {"summary": summary}
        if description:
            req["description"] = description
        if extra:
            req["extra"] = extra
        if due:
            req["due"] = due
        if origin:
            req["origin"] = origin
        if can_edit:
            req["can_edit"] = can_edit

        task_info = self.client.request(
            "POST", "/task/v1/tasks", data=json.dumps(req), params=params
        )
        task_id = task_info["data"]["task"]["id"]

        if collaborators:
            task_info = self.client.request(
                "POST",
                "/task/v1/tasks/{}/collaborators".format(task_id),
                data=json.dumps(collaborators),
            )

        return task_info

    def get_task_collaborators(self, task_id):
        return self.client.request(
            "GET",
            "/task/v1/tasks/{}/collaborators".format(task_id)
        )

    def add_task_collaborators(self, task_id, collaborators):
        return self.client.request(
            "POST",
            "/task/v1/tasks/{}/collaborators".format(task_id),
            data=json.dumps(collaborators),
        )

    def remove_task_collaborators(self, task_id, collaborators):

        return self.client.request(
            "POST",
            "/task/v1/tasks/{}/batch_delete_collaborator".format(task_id),
            data=json.dumps(collaborators),
        )

    def update_task(self, task_id, update_fields, task):

        payload = {"task": task, "update_fields": update_fields}
        headers = {"Content-Type": "application/json; charset=utf-8"}
        return self.client.request(
            "PATCH",
            "/task/v1/tasks/{}".format(task_id),
            data=json.dumps(payload),
            headers=headers,
        )

    def complete_task(self, task_id):
        return self.client.request("POST", "/task/v1/tasks/{}/complete".format(task_id))

    def uncomplete_task(self, task_id):
        return self.client.request(
            "POST", "/task/v1/tasks/{}/uncomplete".format(task_id)
        )

    def delete_task(self, task_id):
        return self.client.request("DELETE", "/task/v1/tasks/{}".format(task_id))
