import registerExtension from "./index.js";

export class JsonLoader {
  json_file;
  data;
  verifyVideoSRC;
  name;
  status;
  error;

  constructor(json_file, verifyVideoSRC = true, name = "Local Files") {
    this.json_file = json_file;
    this.verifyVideoSRC = verifyVideoSRC;
    this.name = name;
  }

  async load() {
    console.debug("Loading JSON Loader...");
    if (typeof this.json_file !== "string") {
      this.error = "Error: `json_file` must be valid string";
      this.status = "error";
      console.error(this.error);
      return;
    }
    await fetch(this.json_file)
      //check if response is ok
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        registerExtension({
          type: "json_file",
          name: this.name,
          verifyVideoSRC: this.verifyVideoSRC,
          data: json,
        });
        this.data = json;
        this.status = "success";
      })
      .catch((error) => {
        console.error("Error:", error);
        this.status = "error";
        this.error = error;
      });
  }
}
