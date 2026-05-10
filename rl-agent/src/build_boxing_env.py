import xmltodict
from pathlib import Path

CABLE_LENGTH = 2.83
CABLE_WIDTH = 0.05
STIFFNESS = 400 # Angular resistance to bending, main control
DAMPING = 5 # Energy dissipation to avoid indefinite bouncing
ARMATURE = 0.01 # For numerical stability

ROPE_TEMPLATE = """<composite type="cable" curve="s" count="16 1 1" size="{cable_length}" prefix="{prefix}" initial="free" offset="{offset}" quat="{rotation}">
    <geom type="capsule" size="{cable_width}" contype="2" conaffinity="1"/>
    <joint stiffness="{stiffness}" damping="{damping}" armature="{armature}" kind="main"/>
    <site />
</composite>"""

ROOT_DIR = Path(__file__).parent.parent
with open(ROOT_DIR / "assets/mujoco_envs/boxing_ring.xml", "r") as f:
    data = xmltodict.parse(f.read())

poles = {}
poles_names = ["pole_bottom_left", "pole_bottom_right", "pole_top_left", "pole_top_right"]

# Store the poles for taking their site's positions
for body in data["mujoco"]["worldbody"]["body"]:
    if body["@name"] in poles_names:
        poles[body["@name"]] = body

# Create the ropes and connections for the bottom_left and top_right poles based on the site's positions'
composite_list = []
connection_list = []

def create_ropes(pole_name, rotated_prefix, quat_rotation, identity_rotation):
    global composite_list
    global connection_list
    global poles

    for site in poles[pole_name]["site"]:
        start_pole, dest_pole, num = site["@name"].split("-")
        cable_prefix = f"c-{site["@name"]}_"

        # Buld the rope
        if dest_pole == rotated_prefix:
            rotation = quat_rotation
        else:
            rotation = identity_rotation

        pole_pos = [float(x) for x in poles[pole_name]["@pos"].split(" ")]
        site_pos = [float(x) for x in site["@pos"].split(" ")]
        offset = " ".join([str(round(zipped[0] + zipped[1], 2)) for zipped in zip(pole_pos, site_pos)])

        formatted_rope = ROPE_TEMPLATE.format(
            cable_length=CABLE_LENGTH,
            cable_width=CABLE_WIDTH,
            stiffness=STIFFNESS,
            damping=DAMPING,
            armature=ARMATURE,
            offset=offset,
            rotation=rotation,
            prefix=cable_prefix
        )
        formatted_rope_dict = xmltodict.parse(formatted_rope)
        composite_list.append(formatted_rope_dict["composite"])

        # Build the connection
        dest_site = f"{dest_pole}-{start_pole}-{num}"
        connection_list.append({"@site1": f"{cable_prefix}S_first", "@site2": site["@name"]})
        connection_list.append({"@site1": f"{cable_prefix}S_last", "@site2": dest_site})

create_ropes("pole_bottom_left", "tl", "0.7071 0 0 0.7071", "1 0 0 0")
# Cable goes in opposite direction
create_ropes("pole_top_right", "br", "0.7071 0 0 -0.7071", "0 0 1 0")

# Store the XML
data["mujoco"]["worldbody"]["composite"] = composite_list
data["mujoco"]["equality"] = {"connect": connection_list}
with open(ROOT_DIR / "assets/mujoco_envs/boxing_ring_with_ropes.xml", "w") as f:
    f.write(xmltodict.unparse(data, pretty=True))