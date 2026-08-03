/*
 * Copyright 2012-2019 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.springframework.samples.petclinic.system;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;
import org.springframework.core.env.Environment;

/**
 * Verifies that the values configured in {@code application.properties} are actually
 * applied to the Spring context, including placeholder resolution (e.g.
 * {@code ${database}}).
 */
@SpringBootTest(webEnvironment = WebEnvironment.NONE)
class ApplicationPropertiesTests {

	@Autowired
	private Environment env;

	@Test
	void databaseDefaultsToH2() {
		assertThat(env.getProperty("database")).isEqualTo("h2");
	}

	@Test
	void schemaAndDataLocationsAreResolvedFromDatabaseProperty() {
		assertThat(env.getProperty("spring.sql.init.schema-locations")).isEqualTo("classpath*:db/h2/schema.sql");
		assertThat(env.getProperty("spring.sql.init.data-locations")).isEqualTo("classpath*:db/h2/data.sql");
	}

	@Test
	void thymeleafModeIsHtml() {
		assertThat(env.getProperty("spring.thymeleaf.mode")).isEqualTo("HTML");
	}

	@Test
	void jpaSettingsDoNotAutoGenerateSchemaAndKeepSessionOpenInView() {
		assertThat(env.getProperty("spring.jpa.hibernate.ddl-auto")).isEqualTo("none");
		assertThat(env.getProperty("spring.jpa.open-in-view", Boolean.class)).isTrue();
	}

	@Test
	void messagesBasenameIsConfigured() {
		assertThat(env.getProperty("spring.messages.basename")).isEqualTo("messages/messages");
	}

	@Test
	void allActuatorEndpointsAreExposed() {
		assertThat(env.getProperty("management.endpoints.web.exposure.include")).isEqualTo("*");
	}

	@Test
	void defaultLoggingLevelIsInfo() {
		assertThat(env.getProperty("logging.level.org.springframework")).isEqualTo("INFO");
	}

	@Test
	void staticResourcesAreCachedForTwelveHours() {
		assertThat(env.getProperty("spring.web.resources.cache.cachecontrol.max-age")).isEqualTo("12h");
	}

}
