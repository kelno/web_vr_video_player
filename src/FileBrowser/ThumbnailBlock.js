import { Block } from "three-mesh-ui";

import * as MAIN from "../index.js";

export default class ThumbnailBlock extends Block {
    fileSRC;
    fileNameButton;
    fileThumbnail;
    screen_type;
    constructor(
        options,
        fileSRC,
        fileNameButton,
        fileThumbnail,
        screen_type,
        frame_height,
        frame_width,
        selectedAttributes,
        hoveredStateAttributes,
        idleStateAttributes
    ) {
        super(options);

        this.fileSRC = fileSRC;
        this.fileNameButton = fileNameButton;
        this.fileThumbnail = fileThumbnail;
        this.screen_type = screen_type;
        this.frame_height = frame_height;
        this.frame_width = frame_width;
        this.setupState({
            state: "selected",
            attributes: selectedAttributes,
            onSet: () => {
                if (screen_type === "screen")
                    MAIN.scaleScreenMesh(
                        this.frame_width / this.frame_height
                    );
                if (screen_type === "tb_screen")
                    MAIN.scaleTBScreenMesh(
                        this.frame_width / this.frame_height
                    );

                MAIN.requestVideoPlayback(this.fileSRC, this.screen_type);
            },
        });

        this.setupState({
            state: "hovered",
            attributes: hoveredStateAttributes,
        });
        this.setupState({
            state: "idle",
            attributes: idleStateAttributes,
        });
    }
}
