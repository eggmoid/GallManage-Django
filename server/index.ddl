CREATE INDEX BPOST_NAME_IDX ON BPOST(UPPER(NAME));
CREATE INDEX BPOST_IDIP_IDX ON BPOST(UPPER(IDIP));

CREATE INDEX POST_NAME_IDX ON POST(UPPER(NAME));
CREATE INDEX POST_IDIP_IDX ON POST(UPPER(IDIP));
