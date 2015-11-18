

ratpack {
  handlers {
    post('vote') {
      parse(JsonNode).then { JsonNode jsonRequest ->
        render json(message: 'OK')
      }
    }
  }
}



