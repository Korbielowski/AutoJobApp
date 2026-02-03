import { Title } from "@solidjs/meta";
import {GET} from "@solidjs/start";
import {client} from "../../api/client";

function draw_job(data) {
    let jobContainer = document.getElementById("job-entries-container");
    if (!jobContainer){
        return;
    }

    let li = document.createElement("li");

    li.innerHTML = `
            <div>
                <h5>Job Title: </h5>
                <p class="job-data">${data.title}</p>
                <br>
                <h5>Location: </h5>
                <p class="job-data">${data.location}</p>
                <br>
                <h5>Company Name: </h5>
                <p class="job-data">${data.company_name}</p>
            </div>
            <details>
                <div class="job-data-container">
                    <h5>CV Path: </h5>
                    <p>${data.cv_path}</p>
                </div>
                <summary>Job details</summary>
                <div class="job-data-container">
                    <h5>Job Url: </h5>
                     <p>
                         <a href="${data.job_url}" target="_blank">${data.job_url}</a>
                     </p>
                </div>
                <div class="job-data-container">
                    <h5>Company Url: </h5>
                    <p>
                        <a href="${data.company_url}" target="_blank">${data.company_url}</a>
                    </p>
                </div>
                <div class="job-data-container">
                    <h5>Contract Type: </h5>
                    <p class="job-data">${data.contract_type}</p>
                </div>
                <div class="job-data-container">
                    <h5>Employment Type: </h5>
                    <p class="job-data">${data.employment_type}</p>
                </div>
                <div class="job-data-container">
                    <h5>Work Arrangement: </h5>
                    <p class="job-data">${data.work_arrangement}</p>
                </div>
                <div class="job-data-container">
                    <h5>Job Requirements: </h5>
                    <p class="job-data">${data.requirements}</p>
                </div>
                <div class="job-data-container">
                    <h5>Duties: </h5>
                    <p class="job-data">${data.duties}</p>
                </div>
                <div class="job-data-container">
                    <h5>About Project: </h5>
                    <p class="job-data">${data.about_project}</p>
                </div>
                <div class="job-data-container">
                    <h5>Company Benefits: </h5>
                    <p class="job-data">${data.offer_benefits}</p>
                </div>
                <div class="job-data-container">
                    <h5>Additional Information: </h5>
                    <p class="job-data">${data.additional_information}</p>
                </div>
            </details>
        `;
    jobContainer.appendChild(li);
}

let eventSrc: EventSource | null = null;

async function scrape_jobs(){
    const scrapeBtn = document.getElementById("scrape-btn");
    const statusDot = document.getElementById("status-dot");

    if(! scrapeBtn || !statusDot){
        return;
    }

    if (scrapeBtn.innerText === "Start job search") {
        const response = await client.GET("/scrape_jobs_check")

        if(!response){
            return;
        }

         eventSrc = new EventSource("http://127.0.0.1:8000/");

        eventSrc.onmessage = function (event) {
            const data = JSON.parse(event.data);
            if (data === null && eventSrc) {
                scrapeBtn.innerText = "Start job search";
                eventSrc.close();
                eventSrc = null;
                return;
            }
            draw_job(data);
        };

        statusDot.className = "status-dot-alive";
        scrapeBtn.innerText = "Stop job search";
    } else {
        if (eventSrc){
            eventSrc.close();
            eventSrc = null;
        }
        scrapeBtn.innerText = "Start job search";
        statusDot.className = "status-dot-dead";
    }
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
                      <p id="status-text">Run Status<span class="status-dot-dead"
                          id="status-dot"></span></p>
                  </div>
              </div>
          </div>
      </main>
  );
}
