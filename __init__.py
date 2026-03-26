import subprocess
import sys, os
import platform, urllib.request, zipfile, shutil

# 1. Dependency check and installation logic (from user sample)
def ensure_aria2_installed():
    system = platform.system().lower()
    if system == "windows":
        try:
            subprocess.run(["aria2c", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ aria2c not found. Installing...")

        aria2_url = "https://github.com/aria2/aria2/releases/download/release-1.36.0/aria2-1.36.0-win-64bit-build1.zip"
        temp_zip = os.path.join(os.environ["TEMP"], "aria2.zip")
        install_dir = os.path.join(os.path.dirname(__file__), "bin", "aria2")

        try:
            urllib.request.urlretrieve(aria2_url, temp_zip)
            if os.path.exists(install_dir):
                shutil.rmtree(install_dir)
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall(install_dir)
            os.environ["PATH"] += os.pathsep + install_dir
            print("✅ aria2c installed successfully!")
        except Exception as e:
            print("❌ Failed to install aria2c:", e)
    elif system == "linux":
        try:
            subprocess.check_call(["sudo", "apt", "install", "-y", "fonts-jetbrains-mono"])
        except Exception as e:
            print("❌ Error installing Linux dependencies:", e)

# ensure_aria2_installed() # Optional: Uncomment if you need it

def check_pip(package_name):
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
    
def install():
    file_check = os.path.join(os.path.dirname(__file__), "installed.txt")
    list_check = os.path.join(os.path.dirname(__file__), "requirements.txt")
    
    if not os.path.exists(list_check):
        return

    expected_content = ""
    with open(list_check, 'r', encoding='utf-8') as file:
        expected_content = file.read()
    
    installed_content = ""
    if os.path.exists(file_check):
        with open(file_check, 'r', encoding='utf-8') as file:
            installed_content = file.read()
            
    if installed_content != expected_content:
        list_package = expected_content.splitlines()
        for package_name in list_package:
            package_name = package_name.strip()
            if package_name and not package_name.startswith("#"):
                if not check_pip(package_name):
                    print(f"Installing missing dependency: {package_name}")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        
        with open(file_check, "w", encoding='utf-8') as file:
            file.write(expected_content)

# Start installation
install()

# 2. Node imports
from .node.backend import NODE_CLASS_MAPPINGS as backend_node, NODE_DISPLAY_NAME_MAPPINGS as backend_dis
from .node.trigger import NODE_CLASS_MAPPINGS as trigger_node, NODE_DISPLAY_NAME_MAPPINGS as trigger_dis
from .node.status import NODE_CLASS_MAPPINGS as status_node, NODE_DISPLAY_NAME_MAPPINGS as status_dis
from .node.webhook import NODE_CLASS_MAPPINGS as webhook_node, NODE_DISPLAY_NAME_MAPPINGS as webhook_dis
from .node.automation import NODE_CLASS_MAPPINGS as automation_node, NODE_DISPLAY_NAME_MAPPINGS as automation_dis
from .node.vision import NODE_CLASS_MAPPINGS as vision_node, NODE_DISPLAY_NAME_MAPPINGS as vision_dis
from .node.extension_bridge import NODE_CLASS_MAPPINGS as extension_node, NODE_DISPLAY_NAME_MAPPINGS as extension_dis
from .node.image_utils import NODE_CLASS_MAPPINGS as image_node, NODE_DISPLAY_NAME_MAPPINGS as image_dis
from .node.video_utils import NODE_CLASS_MAPPINGS as video_node, NODE_DISPLAY_NAME_MAPPINGS as video_dis
from .node.photoshop_bridge import NODE_CLASS_MAPPINGS as ps_node, NODE_DISPLAY_NAME_MAPPINGS as ps_dis
from .node.llm_utils import NODE_CLASS_MAPPINGS as llm_node, NODE_DISPLAY_NAME_MAPPINGS as llm_dis
from .node.utility_nodes import NODE_CLASS_MAPPINGS as util_node, NODE_DISPLAY_NAME_MAPPINGS as util_dis

NODE_CLASS_MAPPINGS = {
    **backend_node,
    **trigger_node,
    **status_node,
    **webhook_node,
    **automation_node,
    **vision_node,
    **extension_node,
    **image_node,
    **video_node,
    **ps_node,
    **llm_node,
    **util_node
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **backend_dis,
    **trigger_dis,
    **status_dis,
    **webhook_dis,
    **automation_dis,
    **vision_dis,
    **extension_dis,
    **image_dis,
    **video_dis,
    **ps_dis,
    **llm_dis,
    **util_dis
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
