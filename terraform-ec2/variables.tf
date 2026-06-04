variable "aws_region" {
  default = "us-east-1"
}

variable "instance_name" {
  default = "dev-server"
}

variable "instance_count" {
  type    = number
  default = 1
}

variable "key_name" {
  description = "Existing AWS Key Pair"
}

variable "instance_type" {
  default = "t3.micro"
}

variable "architecture" {
  description = "CPU architecture: x86 or arm"
  type        = string
  default     = "x86"
}

