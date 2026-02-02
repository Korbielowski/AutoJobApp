import { Title } from "@solidjs/meta";

function scrape_jobs(){

}

export default function Home() {
  return (
      <main class="text-slate-100">
          <Title>AutoJobApp</Title>
          <div class="">
              <div id="run-container" class="flex flex-col gap-2">
                  <details>
                      <summary class="select-none">Run Options</summary>

                      <form id="scraping-form">
                          <div>
                              <input
                                  type="checkbox"
                                  id="generate-cover-letter"
                                  name="generate_cover_letter"
                              />
                              <label for="generate-cover-letter"
                              >Option whether to generate cover letter</label
                              >
                          </div>
                          <hr/>
                          <div id="llm-generation-container">
                              <div>
                                  <input
                                      type="radio"
                                      id="llm-generation"
                                      name="cv_creation_mode"
                                      value="llm-generation"
                                      checked
                                  />
                                  <label for="llm-generation">Generate CV
                                      using LLM</label>
                              </div>
                              <div>
                                  <input
                                      type="radio"
                                      id="llm-selection"
                                      name="cv_creation_mode"
                                      value="llm-selection"
                                  />
                                  <label for="llm-selection"
                                  >Let LLM select skills and insert them into
                                      template</label
                                  >
                              </div>
                              <div>
                                  <input
                                      type="radio"
                                      id="no-llm-generation"
                                      name="cv_creation_mode"
                                      value="no-llm-generation"
                                  />
                                  <label for="no-llm-generation"
                                  >Let application insert skills into CV
                                      template</label
                                  >
                              </div>
                              <div>
                                  <input
                                      type="radio"
                                      id="user-specified"
                                      name="cv_creation_mode"
                                      value="user-specified"
                                  />
                                  <label for="user-specified">Use CV created
                                      by the user</label>
                              </div>
                          </div>
                          <div id="cv-file-container" hidden>
                              <input type="file" id="cv-file" name="cv_file"
                                     accept=".pdf"/>
                              <label for="cv-file">CV file to use</label>
                          </div>
                          <hr/>
                          <div>
                              <input
                                  type="number"
                                  id="retries"
                                  name="retries"
                                  min="1"
                                  max="10"
                                  value="3"
                              />
                              <label for="retries">Number of retries</label>
                          </div>
                          <div>
                              <button id="save-preferences-btn">Save
                                  preferences
                              </button>
                          </div>
                      </form>
                  </details>
                  <div id="scrape-btn-container" class="flex justify-between max-w-2/12 items-end">
                      <button onClick={scrape_jobs} id="scrape-btn" class="normal-btn">Start job
                          search
                      </button>
                      <p id="status-text">Run Status <span
                          id="status-dot"></span></p>
                  </div>
              </div>
          </div>
      </main>
  );
}
