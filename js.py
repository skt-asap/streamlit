from folium.map import Marker
from jinja2 import Template

def set_marker_click_template():
    click_marker = """
    {% macro script(this, kwargs) %}

    function copyToClipboard(text) {
      navigator.clipboard.writeText(text).then(function() {
        console.log("클립보드에 복사되었습니다: ", text);
      }, function(err) {
        console.error("클립보드 복사에 실패했습니다: ", err);
      });
    }

    function showToast() {
      var toast = document.getElementById("toast");
      toast.style.visibility = "visible";
      setTimeout(function() {
        toast.style.visibility = "hidden";
      }, 3000);
    }

    function onClick(e) {
        var marker = e.target;
        if (marker.getTooltip()) {
            var cellID = marker.getTooltip().getElement().innerText.trim();
            copyToClipboard(cellID);
        }
    }

    var {{ this.get_name() }} = L.marker(
        {{ this.location|tojson }},
        {{ this.options|tojson }}
    ).addTo({{ this._parent.get_name() }}).on('click', onClick);

    {% endmacro %}
    """

    Marker._template = Template(click_marker)

