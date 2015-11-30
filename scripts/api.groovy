@Grab("org.slf4j:slf4j-simple:1.7.13")
@Grab("io.ratpack:ratpack-groovy:1.1.1")
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import com.fasterxml.jackson.databind.JsonNode
import static ratpack.groovy.Groovy.ratpack
import static ratpack.handling.RequestLogger.ncsa
import static ratpack.jackson.Jackson.json

ratpack {
  bindings {
    add LoggerFactory.getLogger('data-api')
  }
  handlers {
    all(ncsa())
    post('vote') {
      parse(JsonNode).blockingOp { JsonNode jsonRequest ->
        jsonRequest
      }.then {
        render json(message: 'OK')
      }.onError {
        response.status = 500
        render json(message: 'ERROR')
      }
    }
    get {
      render "Data Collection API!"
    }
  }
}



