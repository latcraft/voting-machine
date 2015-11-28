

ratpack {
  handlers {
    post('vote') {
      parse(JsonNode).then { JsonNode jsonRequest ->
        jsonRequest
        render json(message: 'OK')
      }
    }
  }
}



