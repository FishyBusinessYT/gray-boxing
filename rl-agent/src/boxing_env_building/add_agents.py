import xmltodict
import copy

agent_parts = set()
props_to_rename = ("@name", "@joint", "@body1", "@body2")

def add_prefix(node, prefix):
    # Rename the node
    for prop in props_to_rename:
        if node.get(prop) and (node[prop] in agent_parts or prop == "@name"):
            node[prop] = f"{prefix}_{node[prop]}"
            # Don't break. There may be more props to rename

    # Search for children to rename
    for child_key in node.keys():
        if type(node[child_key]) is dict:
            add_prefix(node[child_key], prefix)
        elif type(node[child_key]) is list:
            for child in node[child_key]:
                add_prefix(child, prefix)

def append_or_create(env, key, values):
    if key in env:
        env[key].extend(values)
    else:
        env[key] = values

def add_agents(env_dict, agent_dir):
    with open(agent_dir, "r") as f:
        agent = xmltodict.parse(f.read())

    # Collect the agent's parts names for future renaming
    def collect_parts(node):
        global agent_parts

        if node.get("@name"):
            agent_parts.add(node["@name"])
        for child_key in node.keys():
            if type(node[child_key]) is dict:
                collect_parts(node[child_key])
            elif type(node[child_key]) is list:
                for child in node[child_key]:
                    collect_parts(child)

    collect_parts(agent["mujoco"]["worldbody"]["body"])

    # Add duplicate agents to the xml
    agent_torso = agent["mujoco"]["worldbody"]["body"]
    a1_torso = copy.deepcopy(agent_torso)
    a2_torso = copy.deepcopy(agent_torso)
    # Move the agents to the right position
    a1_torso["@pos"] = "1 0 1.625"
    a2_torso["@pos"] = "-1 0 1.625"
    a2_torso["@euler"] = "0 0 0"
    # Prefix the names
    add_prefix(a1_torso, "a1")
    add_prefix(a2_torso, "a2")
    # Add the agents to the xml
    env_dict["mujoco"]["worldbody"]["body"].append(a1_torso)
    env_dict["mujoco"]["worldbody"]["body"].append(a2_torso)

    # Duplicate and add tendons
    tendons = agent["mujoco"]["tendon"]
    a1_tendons = copy.deepcopy(tendons)
    a2_tendons = copy.deepcopy(tendons)
    add_prefix(a1_tendons, "a1")
    add_prefix(a2_tendons, "a2")
    append_or_create(env_dict["mujoco"], "tendon", [a1_tendons, a2_tendons])

    # Duplicate and add contacts
    sites = agent["mujoco"]["contact"]
    a1_contact = copy.deepcopy(sites)
    a2_contact = copy.deepcopy(sites)
    add_prefix(a1_contact, "a1")
    add_prefix(a2_contact, "a2")
    append_or_create(env_dict["mujoco"], "contact", [a1_contact, a2_contact])

    # Duplicate and add actuators
    actuators = agent["mujoco"]["actuator"]
    a1_actuators = copy.deepcopy(actuators)
    a2_actuators = copy.deepcopy(actuators)
    add_prefix(a1_actuators, "a1")
    add_prefix(a2_actuators, "a2")
    append_or_create(env_dict["mujoco"], "actuator", [a1_actuators, a2_actuators])

    return env_dict