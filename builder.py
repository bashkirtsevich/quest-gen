import os
import yaml
import codecs
from jinja2 import Environment, FileSystemLoader
from distutils.dir_util import copy_tree
from shutil import copyfile
from functools import partial


def render(env, template_name, **kwargs):
    return env.get_template(template_name).render(**kwargs)


def main(scenario_path, static_path, templates_path, out_path):
    templates_env = Environment(
        loader=FileSystemLoader(templates_path),
        trim_blocks=True
    )

    render_ = partial(render, templates_env)

    with codecs.open(scenario_path, encoding="utf-8") as file:
        scenario = yaml.load(file)
        # TODO: validate yaml

    scenario_dir = os.path.dirname(scenario_path)

    quest_info = scenario["quest_info"]

    project_path = os.path.join(out_path, quest_info["name"])

    print("Making release dir:", project_path)
    os.makedirs(project_path, exist_ok=True)

    print("Copy common static files")
    copy_tree(static_path, project_path)

    print("Make index page")
    with open(os.path.join(project_path, "index.html"), "w") as file:
        print(
            render_("index.html", quest_info=quest_info),
            file=file
        )

    cover_path = scenario.get("quest_cover", None)
    if cover_path:
        print("Copy quest cover")
        copyfile(os.path.join(scenario_dir, cover_path), os.path.join(project_path, "img/cover.jpg"))

    print("Creating quest tree")
    frames = scenario["quest_frames"]
    images = scenario.get("quest_images", {})

    for frame_name, frame in frames.items():
        image_path = images.get(frame.get("image", None), None)
        if image_path:
            copyfile(os.path.join(scenario_dir, image_path), os.path.join(project_path, f"img/{frame_name}.jpg"))

        with open(os.path.join(project_path, f"{frame_name}.html"), "w") as file:
            print(
                render_("frame.html",
                        quest_info=quest_info,
                        frame=frame,
                        frame_name=frame_name,
                        image_path=f"img/{frame_name}.jpg" if image_path else None),
                file=file
            )


if __name__ == '__main__':
    main("scenario/pdh_quest.yml", "static", "templates", "quests")
